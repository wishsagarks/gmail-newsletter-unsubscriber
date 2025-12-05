"""
Streamlit UI components for automation scheduler
"""

import streamlit as st
from automation_scheduler import AutomationScheduler


def render_automation_reminder(scheduler: AutomationScheduler):
    """Render reminder banner when cleanup is due"""
    if scheduler.should_show_reminder():
        st.warning(
            f"⏰ **Scheduled Cleanup Due!**\n\n"
            f"Your {scheduler.get_frequency_label().lower()} newsletter cleanup is ready to run.\n\n"
            f"Last run: {scheduler.format_last_run()}"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🚀 Run Now", use_container_width=True):
                scheduler.dismiss_reminder()
                return "run_now"
        with col2:
            if st.button("⏭️ Remind Me Later", use_container_width=True):
                scheduler.dismiss_reminder()
                st.rerun()
    
    return None


def render_automation_settings(scheduler: AutomationScheduler):
    """Render automation settings in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 Automation Settings")
    
    # Enable/Disable toggle
    enabled = st.sidebar.toggle(
        "Enable Automatic Cleanup",
        value=scheduler.is_enabled(),
        help="Automatically run newsletter cleanup on schedule"
    )
    
    if enabled != scheduler.is_enabled():
        scheduler.set_enabled(enabled)
        scheduler.update_kiro_hook()
        st.sidebar.success("✓ Settings saved!")
    
    # Frequency selector
    if enabled:
        frequency_options = {
            "daily": "Daily (Every day)",
            "weekly": "Weekly (Every Monday)",
            "biweekly": "Bi-weekly (Every 2 weeks)",
            "monthly": "Monthly (1st of month)",
        }
        
        current_freq = scheduler.get_frequency()
        frequency = st.sidebar.selectbox(
            "Cleanup Frequency",
            options=list(frequency_options.keys()),
            format_func=lambda x: frequency_options[x],
            index=list(frequency_options.keys()).index(current_freq),
            help="How often to automatically run cleanup"
        )
        
        if frequency != current_freq:
            scheduler.set_frequency(frequency)
            scheduler.update_kiro_hook()
            st.sidebar.success("✓ Frequency updated!")
        
        # Show schedule info
        st.sidebar.info(
            f"📅 **Next Run:** {scheduler.format_next_run()}\n\n"
            f"🕐 **Last Run:** {scheduler.format_last_run()}"
        )
        
        # Kiro integration info
        with st.sidebar.expander("🔧 Kiro Integration"):
            st.markdown("""
            **Automation is powered by Kiro!**
            
            - ✅ Workflow: `scan_and_unsubscribe_gmail`
            - ✅ Hook: `auto_newsletter_cleanup`
            - ✅ Scheduled runs via Kiro
            
            Your settings are synced with Kiro hooks automatically.
            """)
    else:
        st.sidebar.info(
            "Enable automation to schedule regular cleanups.\n\n"
            "Your inbox will be cleaned automatically!"
        )


def render_automation_stats(scheduler: AutomationScheduler):
    """Render automation statistics"""
    stats = scheduler.get_stats()
    
    st.markdown("### 📊 Automation Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Runs",
            stats["total_runs"],
            help="Total number of automated cleanups"
        )
    
    with col2:
        st.metric(
            "Last Cleanup",
            scheduler.format_last_run(),
            help="When the last cleanup ran"
        )
    
    with col3:
        st.metric(
            "Next Cleanup",
            scheduler.format_next_run(),
            help="When the next cleanup is scheduled"
        )
    
    with col4:
        st.metric(
            "Last Unsubscribed",
            stats["last_unsubscribed_count"],
            help="Newsletters unsubscribed in last run"
        )
    
    if stats["enabled"]:
        st.success(
            f"✅ Automation is **enabled** - Running {stats['frequency'].lower()}"
        )
    else:
        st.info(
            "ℹ️ Automation is **disabled** - Enable in sidebar to schedule automatic cleanups"
        )


def render_first_run_setup(scheduler: AutomationScheduler):
    """Render first-run automation setup"""
    if scheduler.get_last_run() is None:
        st.info(
            "👋 **First time here?**\n\n"
            "After your first cleanup, you can enable automatic scheduling "
            "to keep your inbox clean without lifting a finger!"
        )
        return True
    return False
