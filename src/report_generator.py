"""Generate summary reports."""

from datetime import datetime
from typing import Dict, List
import os
from config import OUTPUT_DIR, SUMMARY_FILE


class ReportGenerator:
    """Generates summary reports of unsubscribe actions."""
    
    def __init__(self):
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def generate_summary(self, stats: Dict, results: List[Dict]) -> str:
        """
        Generate markdown summary report.
        
        Args:
            stats: Overall statistics dict
            results: List of execution results
        
        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""# Gmail Newsletter Unsubscribe Summary

**Generated:** {timestamp}

## Overview

- **Total messages scanned:** {stats['total_scanned']}
- **Newsletter senders detected:** {stats['senders_detected']}
- **Approved for unsubscribe:** {stats['approved']}
- **Skipped:** {stats['skipped']}
- **Kept (whitelisted):** {stats['kept']}

---

## Unsubscribe Results

"""
        
        # Group results by action type
        successful = [r for r in results if r['result']['success']]
        failed = [r for r in results if not r['result']['success']]
        manual_review = [r for r in results if r['result'].get('action') == 'manual_review']
        
        # Successful unsubscribes
        if successful:
            report += f"### ✓ Successfully Unsubscribed ({len(successful)})\n\n"
            for r in successful:
                sender = r['sender']
                result = r['result']
                report += f"- **{sender['display_name']}** <{sender['email']}>\n"
                report += f"  - Messages: {sender['messages_count']}\n"
                report += f"  - Method: {result['action']}\n"
                report += f"  - Status: {result['message']}\n\n"
        
        # Failed attempts
        if failed and not manual_review:
            report += f"### ✗ Failed Unsubscribes ({len(failed)})\n\n"
            for r in failed:
                sender = r['sender']
                result = r['result']
                report += f"- **{sender['display_name']}** <{sender['email']}>\n"
                report += f"  - Error: {result['message']}\n\n"
        
        # Manual review needed
        if manual_review:
            report += f"### ⚠ Manual Review Required ({len(manual_review)})\n\n"
            report += "These senders require manual action (login or web form):\n\n"
            for r in manual_review:
                sender = r['sender']
                report += f"- **{sender['display_name']}** <{sender['email']}>\n"
                if sender.get('unsubscribe_url'):
                    report += f"  - URL: {sender['unsubscribe_url']}\n"
                report += f"  - Messages: {sender['messages_count']}\n\n"
        
        report += "\n---\n\n"
        report += "## Privacy Notice\n\n"
        report += "This report contains only sender information and action summaries. "
        report += "No email content or personal data has been stored.\n"
        
        # Write report
        with open(SUMMARY_FILE, 'w') as f:
            f.write(report)
        
        print(f"\n✓ Summary report saved to: {SUMMARY_FILE}")
        return SUMMARY_FILE
    
    def print_console_summary(self, stats: Dict, results: List[Dict]):
        """Print a brief summary to console."""
        print("\n" + "="*70)
        print("EXECUTION SUMMARY")
        print("="*70)
        print(f"Total messages scanned: {stats['total_scanned']}")
        print(f"Newsletter senders detected: {stats['senders_detected']}")
        print(f"Approved for unsubscribe: {stats['approved']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"Kept (whitelisted): {stats['kept']}")
        print("-"*70)
        
        successful = sum(1 for r in results if r['result']['success'])
        failed = sum(1 for r in results if not r['result']['success'])
        
        print(f"Successfully unsubscribed: {successful}")
        print(f"Failed or manual review: {failed}")
        print("="*70 + "\n")
