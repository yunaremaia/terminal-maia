"""Alert system for price alerts and notifications."""

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum
import time


class AlertType(Enum):
    """Alert types."""
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PERCENT_CHANGE = "percent_change"
    VOLUME_SPIKE = "volume_spike"
    RSI_OVERBOUGHT = "rsi_overbought"
    RSI_OVERSOLD = "rsi_oversold"


class AlertPriority(Enum):
    """Alert priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status."""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass
class Alert:
    """Price alert configuration."""
    id: str
    symbol: str
    alert_type: AlertType
    condition: float
    priority: AlertPriority = AlertPriority.MEDIUM
    status: AlertStatus = AlertStatus.ACTIVE
    created_at: str = ""
    triggered_at: Optional[str] = None
    message: str = ""
    callback: Optional[Callable] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class AlertNotification:
    """Alert notification."""
    alert_id: str
    symbol: str
    alert_type: AlertType
    message: str
    priority: AlertPriority
    timestamp: str
    current_value: float
    triggered_condition: float


class AlertManager:
    """Manages price alerts."""
    
    _alert_id_counter = 0
    
    def __init__(self):
        self._alerts: Dict[str, Alert] = {}
        self._notification_handlers: List[Callable] = []
        self._last_prices: Dict[str, float] = {}
        self._running = False
    
    @classmethod
    def _generate_alert_id(cls) -> str:
        """Generate unique alert ID."""
        cls._alert_id_counter += 1
        return f"ALERT{cls._alert_id_counter:06d}"
    
    def create_alert(self, symbol: str, alert_type: AlertType, 
                    condition: float, priority: AlertPriority = AlertPriority.MEDIUM,
                    message: str = "") -> Alert:
        """Create a new alert."""
        alert = Alert(
            id=self._generate_alert_id(),
            symbol=symbol.upper(),
            alert_type=alert_type,
            condition=condition,
            priority=priority,
            message=message or self._generate_message(alert_type, condition)
        )
        
        self._alerts[alert.id] = alert
        return alert
    
    def _generate_message(self, alert_type: AlertType, condition: float) -> str:
        """Generate default alert message."""
        messages = {
            AlertType.PRICE_ABOVE: f"Price above {condition}",
            AlertType.PRICE_BELOW: f"Price below {condition}",
            AlertType.PERCENT_CHANGE: f"Percent change {condition}%",
            AlertType.VOLUME_SPIKE: f"Volume spike {condition}x",
            AlertType.RSI_OVERBOUGHT: f"RSI above {condition}",
            AlertType.RSI_OVERSOLD: f"RSI below {condition}",
        }
        return messages.get(alert_type, "Alert triggered")
    
    def remove_alert(self, alert_id: str) -> bool:
        """Remove an alert."""
        if alert_id in self._alerts:
            del self._alerts[alert_id]
            return True
        return False
    
    def get_alerts(self, symbol: Optional[str] = None, 
                  status: Optional[AlertStatus] = None) -> List[Alert]:
        """Get alerts, optionally filtered."""
        alerts = list(self._alerts.values())
        
        if symbol:
            alerts = [a for a in alerts if a.symbol == symbol.upper()]
        
        if status:
            alerts = [a for a in alerts if a.status == status]
        
        return alerts
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return self.get_alerts(status=AlertStatus.ACTIVE)
    
    def register_notification_handler(self, handler: Callable):
        """Register a notification handler."""
        self._notification_handlers.append(handler)
    
    def _notify(self, notification: AlertNotification):
        """Send notification through registered handlers."""
        for handler in self._notification_handlers:
            try:
                handler(notification)
            except Exception as e:
                print(f"Error in notification handler: {e}")
    
    def check_price_alert(self, symbol: str, current_price: float) -> List[AlertNotification]:
        """Check price-based alerts."""
        notifications = []
        self._last_prices[symbol] = current_price
        
        for alert in self.get_alerts(symbol, AlertStatus.ACTIVE):
            triggered = False
            
            if alert.alert_type == AlertType.PRICE_ABOVE:
                triggered = current_price >= alert.condition
            elif alert.alert_type == AlertType.PRICE_BELOW:
                triggered = current_price <= alert.condition
            
            if triggered:
                notification = AlertNotification(
                    alert_id=alert.id,
                    symbol=symbol,
                    alert_type=alert.alert_type,
                    message=alert.message or f"{symbol} price {alert.alert_type.value}: {current_price:.2f}",
                    priority=alert.priority,
                    timestamp=datetime.now().isoformat(),
                    current_value=current_price,
                    triggered_condition=alert.condition
                )
                
                alert.status = AlertStatus.TRIGGERED
                alert.triggered_at = notification.timestamp
                notifications.append(notification)
                self._notify(notification)
        
        return notifications
    
    def check_percent_change_alert(self, symbol: str, 
                                  current_price: float) -> List[AlertNotification]:
        """Check percent change alerts."""
        notifications = []
        
        if symbol not in self._last_prices:
            return notifications
        
        previous_price = self._last_prices[symbol]
        if previous_price == 0:
            return notifications
        
        percent_change = ((current_price - previous_price) / previous_price) * 100
        
        for alert in self.get_alerts(symbol, AlertStatus.ACTIVE):
            if alert.alert_type == AlertType.PERCENT_CHANGE:
                triggered = abs(percent_change) >= alert.condition
                
                if triggered:
                    notification = AlertNotification(
                        alert_id=alert.id,
                        symbol=symbol,
                        alert_type=alert.alert_type,
                        message=f"{symbol} changed {percent_change:+.2f}%",
                        priority=alert.priority,
                        timestamp=datetime.now().isoformat(),
                        current_value=percent_change,
                        triggered_condition=alert.condition
                    )
                    
                    alert.status = AlertStatus.TRIGGERED
                    alert.triggered_at = notification.timestamp
                    notifications.append(notification)
                    self._notify(notification)
        
        self._last_prices[symbol] = current_price
        return notifications
    
    def cancel_alert(self, alert_id: str) -> bool:
        """Cancel an alert."""
        if alert_id in self._alerts:
            self._alerts[alert_id].status = AlertStatus.CANCELLED
            return True
        return False
    
    def reactivate_alert(self, alert_id: str) -> bool:
        """Reactivate a cancelled alert."""
        if alert_id in self._alerts:
            self._alerts[alert_id].status = AlertStatus.ACTIVE
            return True
        return False
    
    def clear_triggered(self):
        """Remove all triggered alerts."""
        triggered = [aid for aid, a in self._alerts.items() 
                   if a.status == AlertStatus.TRIGGERED]
        for aid in triggered:
            del self._alerts[aid]
    
    def get_alert_stats(self) -> Dict:
        """Get alert statistics."""
        stats = {
            'total': len(self._alerts),
            'active': len(self.get_alerts(status=AlertStatus.ACTIVE)),
            'triggered': len(self.get_alerts(status=AlertStatus.TRIGGERED)),
            'cancelled': len(self.get_alerts(status=AlertStatus.CANCELLED)),
        }
        
        by_priority = {p.value: 0 for p in AlertPriority}
        by_type = {t.value: 0 for t in AlertType}
        
        for alert in self._alerts.values():
            by_priority[alert.priority.value] += 1
            by_type[alert.alert_type.value] += 1
        
        stats['by_priority'] = by_priority
        stats['by_type'] = by_type
        
        return stats


class ConsoleNotificationHandler:
    """Console notification handler."""
    
    def __init__(self):
        self._color_codes = {
            AlertPriority.LOW: "\033[94m",
            AlertPriority.MEDIUM: "\033[93m",
            AlertPriority.HIGH: "\033[91m",
            AlertPriority.CRITICAL: "\033[95m",
        }
    
    def __call__(self, notification: AlertNotification):
        """Handle notification."""
        color = self._color_codes.get(notification.priority, "")
        reset = "\033[0m"
        
        print(f"{color}[ALERT]{reset} {notification.timestamp}")
        print(f"  {notification.message}")
        print(f"  Symbol: {notification.symbol}, Value: {notification.current_value}")


_alert_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """Get global alert manager instance."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager
