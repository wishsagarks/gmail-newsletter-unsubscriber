"""Interactive review interface for user approval."""

from typing import Dict, List
from config import WHITELIST_DOMAINS


class InteractiveReviewer:
    """Handles interactive user review of unsubscribe actions."""
    
    def __init__(self):
        self.whitelist = set(WHITELIST_DOMAINS)
    
    def review_senders(self, senders: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Present senders for review and get user decisions.
        
        Args:
            senders: List of sender info dicts
        
        Returns:
            Dict with 'approved', 'skipped', 'kept' lists
        """
        approved = []
        skipped = []
        kept = []
        
        print("\n" + "="*70)
        print("NEWSLETTER UNSUBSCRIBE REVIEW")
        print("="*70)
        print(f"\nFound {len(senders)} newsletter senders to review.")
        print("\nFor each sender, choose:")
        print("  [U] Unsubscribe - Remove me from this list")
        print("  [S] Skip - Don't unsubscribe this time")
        print("  [K] Keep - Never unsubscribe (add to whitelist)")
        print("  [A] Approve All - Unsubscribe from all remaining")
        print("  [Q] Quit - Stop review and exit")
        print("="*70 + "\n")
        
        approve_all = False
        
        for i, sender in enumerate(senders, 1):
            # Check whitelist
            if sender['domain'] in self.whitelist:
                print(f"[{i}/{len(senders)}] WHITELISTED: {sender['display_name']}")
                kept.append(sender)
                continue
            
            # Display sender info
            print(f"\n[{i}/{len(senders)}] " + "-"*60)
            print(f"Sender: {sender['display_name']}")
            print(f"Email: {sender['email']}")
            print(f"Messages: {sender['messages_count']}")
            print(f"Sample: \"{sender['sample_subject'][:60]}...\"")
            print(f"Unsubscribe: {sender['unsubscribe_type']}")
            if sender.get('unsubscribe_url'):
                url_display = sender['unsubscribe_url'][:70]
                print(f"URL: {url_display}...")
            print(f"Confidence: {sender['confidence']*100:.0f}%")
            
            # Auto-approve if flag is set
            if approve_all:
                print("→ AUTO-APPROVED")
                approved.append(sender)
                continue
            
            # Get user input
            while True:
                choice = input("\n[U]nsub / [S]kip / [K]eep / [A]ll / [Q]uit? ").strip().upper()
                
                if choice == 'U':
                    print("→ Will unsubscribe")
                    approved.append(sender)
                    break
                
                elif choice == 'S':
                    print("→ Skipped")
                    skipped.append(sender)
                    break
                
                elif choice == 'K':
                    print(f"→ Added {sender['domain']} to whitelist")
                    self.whitelist.add(sender['domain'])
                    kept.append(sender)
                    break
                
                elif choice == 'A':
                    print("→ Will unsubscribe from this and all remaining")
                    approved.append(sender)
                    approve_all = True
                    break
                
                elif choice == 'Q':
                    print("\n→ Review stopped by user")
                    return {
                        'approved': approved,
                        'skipped': skipped + senders[i:],  # Add remaining as skipped
                        'kept': kept
                    }
                
                else:
                    print("Invalid choice. Please enter U, S, K, A, or Q.")
        
        print("\n" + "="*70)
        print("REVIEW COMPLETE")
        print("="*70)
        print(f"Approved for unsubscribe: {len(approved)}")
        print(f"Skipped: {len(skipped)}")
        print(f"Kept (whitelisted): {len(kept)}")
        print("="*70 + "\n")
        
        return {
            'approved': approved,
            'skipped': skipped,
            'kept': kept
        }
    
    def confirm_execution(self, approved_count: int) -> bool:
        """Final confirmation before executing unsubscribes."""
        if approved_count == 0:
            print("No senders approved for unsubscribe.")
            return False
        
        print(f"\nAbout to unsubscribe from {approved_count} sender(s).")
        choice = input("Proceed with unsubscribe actions? [Y/n] ").strip().upper()
        
        return choice != 'N'
