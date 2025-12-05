"""
Automation Scheduler for Gmail Newsletter Unsubscriber
Tracks last run time, manages frequency, and integrates with Kiro workflows
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict


class AutomationScheduler:
    """Manages automation scheduling and state persistence"""
    
    STATE_FILE = "output/automation_state.json"
    
    FREQUENCY_OPTIONS = {
        "daily": {"days": 1, "label": "Daily"},
        "weekly": {"days": 7, "label": "Weekly"},
        "biweekly": {"days": 14, "label": "Bi-weekly"},
        "monthly": {"days": 30, "label": "Monthly"},
    }
    
    def __init__(self):
        self.state_file = Path(self.STATE_FILE)
        self.state_file.parent.mkdir(exist_ok=True)
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load automation state from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default state for first run
        return {
            "last_run": None,
            "frequency": "weekly",
            "enabled": False,
            "total_runs": 0,
            "last_unsubscribed_count": 0,
            "reminder_dismissed": False,
        }
    
    def _save_state(self):
        """Persist state to disk"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save automation state: {e}")
    
    def record_run(self, unsubscribed_count: int = 0):
        """Record a successful run"""
        self.state["last_run"] = datetime.now().isoformat()
        self.state["total_runs"] += 1
        self.state["last_unsubscribed_count"] = unsubscribed_count
        self.state["reminder_dismissed"] = False
        self._save_state()
    
    def get_last_run(self) -> Optional[datetime]:
        """Get the last run datetime"""
        if self.state["last_run"]:
            return datetime.fromisoformat(self.state["last_run"])
        return None
    
    def get_next_run(self) -> Optional[datetime]:
        """Calculate next scheduled run time"""
        last_run = self.get_last_run()
        if not last_run or not self.state["enabled"]:
            return None
        
        frequency = self.state["frequency"]
        days = self.FREQUENCY_OPTIONS[frequency]["days"]
        return last_run + timedelta(days=days)
    
    def is_due(self) -> bool:
        """Check if a cleanup is due"""
        if not self.state["enabled"]:
            return False
        
        next_run = self.get_next_run()
        if not next_run:
            return True  # First run
        
        return datetime.now() >= next_run
    
    def days_until_next_run(self) -> Optional[int]:
        """Get days until next scheduled run"""
        next_run = self.get_next_run()
        if not next_run:
            return None
        
        delta = next_run - datetime.now()
        return max(0, delta.days)
    
    def should_show_reminder(self) -> bool:
        """Check if reminder should be shown"""
        if not self.state["enabled"] or self.state["reminder_dismissed"]:
            return False
        
        return self.is_due()
    
    def dismiss_reminder(self):
        """Dismiss the current reminder"""
        self.state["reminder_dismissed"] = True
        self._save_state()
    
    def set_frequency(self, frequency: str):
        """Set automation frequency"""
        if frequency in self.FREQUENCY_OPTIONS:
            self.state["frequency"] = frequency
            self._save_state()
    
    def set_enabled(self, enabled: bool):
        """Enable or disable automation"""
        self.state["enabled"] = enabled
        self._save_state()
    
    def is_enabled(self) -> bool:
        """Check if automation is enabled"""
        return self.state["enabled"]
    
    def get_frequency(self) -> str:
        """Get current frequency setting"""
        return self.state["frequency"]
    
    def get_frequency_label(self) -> str:
        """Get human-readable frequency label"""
        freq = self.state["frequency"]
        return self.FREQUENCY_OPTIONS[freq]["label"]
    
    def get_stats(self) -> Dict:
        """Get automation statistics"""
        return {
            "total_runs": self.state["total_runs"],
            "last_run": self.get_last_run(),
            "next_run": self.get_next_run(),
            "last_unsubscribed_count": self.state["last_unsubscribed_count"],
            "enabled": self.state["enabled"],
            "frequency": self.get_frequency_label(),
        }
    
    def format_last_run(self) -> str:
        """Format last run time for display"""
        last_run = self.get_last_run()
        if not last_run:
            return "Never"
        
        delta = datetime.now() - last_run
        
        if delta.days == 0:
            if delta.seconds < 3600:
                minutes = delta.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif delta.days == 1:
            return "Yesterday"
        elif delta.days < 7:
            return f"{delta.days} days ago"
        else:
            return last_run.strftime("%B %d, %Y")
    
    def format_next_run(self) -> str:
        """Format next run time for display"""
        if not self.state["enabled"]:
            return "Disabled"
        
        next_run = self.get_next_run()
        if not next_run:
            return "Not scheduled"
        
        delta = next_run - datetime.now()
        
        if delta.days < 0:
            return "Overdue"
        elif delta.days == 0:
            return "Today"
        elif delta.days == 1:
            return "Tomorrow"
        else:
            return f"In {delta.days} days"
    
    def generate_kiro_hook_config(self) -> str:
        """Generate Kiro hook configuration based on current settings"""
        frequency = self.state["frequency"]
        
        # Map frequency to cron expressions
        cron_map = {
            "daily": "0 9 * * *",      # Every day at 9 AM
            "weekly": "0 9 * * 1",     # Every Monday at 9 AM
            "biweekly": "0 9 */14 * *", # Every 14 days at 9 AM
            "monthly": "0 9 1 * *",    # First day of month at 9 AM
        }
        
        cron = cron_map.get(frequency, "0 9 * * 1")
        
        return f"""name: auto_newsletter_cleanup
description: Automatically run newsletter unsubscriber {self.get_frequency_label().lower()}

trigger:
  type: schedule
  schedule:
    cron: "{cron}"
    timezone: "America/Los_Angeles"

action:
  type: workflow
  workflow: scan_and_unsubscribe_gmail

message: |
  🧹 Running {self.get_frequency_label().lower()} newsletter cleanup...
  
  Scanning your Gmail for newsletters and unsubscribing automatically.

enabled: {str(self.state["enabled"]).lower()}
notify_on_completion: true
"""
    
    def update_kiro_hook(self):
        """Update Kiro hook file with current settings"""
        hook_file = Path(".kiro/hooks/auto_newsletter_cleanup.yaml")
        hook_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(hook_file, 'w') as f:
                f.write(self.generate_kiro_hook_config())
            return True
        except Exception as e:
            print(f"Warning: Could not update Kiro hook: {e}")
            return False
