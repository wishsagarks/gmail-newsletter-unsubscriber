#!/usr/bin/env python3
"""
Gmail Newsletter Unsubscriber - Main Entry Point

A privacy-first automation to scan Gmail for newsletters and unsubscribe in bulk.
"""

import sys
import argparse
from collections import defaultdict
from typing import Dict, List

from gmail_auth import GmailAuthenticator
from gmail_client import GmailClient
from newsletter_detector import NewsletterDetector
from unsubscribe_extractor import UnsubscribeExtractor
from unsubscribe_executor import UnsubscribeExecutor
from interactive_review import InteractiveReviewer
from report_generator import ReportGenerator
from config import AUTO_LABEL_PROCESSED, LABEL_NAME, DAYS_TO_SCAN, MAX_MESSAGES


def main():
    """Main execution flow."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Gmail Newsletter Unsubscriber')
    parser.add_argument('--auto-approve', action='store_true', 
                       help='Automatically approve all newsletters for unsubscribe')
    parser.add_argument('--days', type=int, default=DAYS_TO_SCAN,
                       help=f'Days to scan (default: {DAYS_TO_SCAN})')
    parser.add_argument('--max-messages', type=int, default=MAX_MESSAGES,
                       help=f'Maximum messages to fetch (default: {MAX_MESSAGES})')
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("GMAIL NEWSLETTER UNSUBSCRIBER")
    print("="*70)
    print("\nA privacy-first automation to help you unsubscribe from spam.")
    if args.auto_approve:
        print("🤖 AUTO-APPROVE MODE: All newsletters will be unsubscribed automatically")
    print("="*70 + "\n")
    
    try:
        # Phase 1: Authentication
        print("Phase 1: Authenticating with Gmail...")
        authenticator = GmailAuthenticator()
        service = authenticator.authenticate()
        gmail_client = GmailClient(service)
        
        # Phase 2: Fetch messages
        print(f"\nPhase 2: Scanning for newsletters (last {args.days} days, max {args.max_messages} messages)...")
        messages = gmail_client.fetch_recent_messages(days=args.days, max_results=args.max_messages)
        
        if not messages:
            print("No messages found matching criteria.")
            return
        
        # Phase 3: Detect newsletters and extract unsubscribe info
        print("Phase 3: Analyzing messages...")
        detector = NewsletterDetector()
        extractor = UnsubscribeExtractor()
        
        # Group by sender
        senders_map = defaultdict(lambda: {
            'messages': [],
            'message_ids': [],
            'subjects': []
        })
        
        for i, msg in enumerate(messages, 1):
            if i % 50 == 0:
                print(f"  Processed {i}/{len(messages)} messages...")
            
            # Get message details
            message = gmail_client.get_message_details(msg['id'])
            if not message:
                continue
            
            # Extract headers
            from_header = gmail_client.get_header(message, 'From') or ''
            subject = gmail_client.get_header(message, 'Subject') or '(no subject)'
            list_unsub = gmail_client.get_header(message, 'List-Unsubscribe') or ''
            
            headers = {
                'from': from_header,
                'subject': subject,
                'list-unsubscribe': list_unsub
            }
            
            # Get body snippet (first 500 chars for detection)
            body = gmail_client.get_body(message)
            body_snippet = body[:500] if body else ''
            
            # Detect if newsletter
            is_newsletter, confidence = detector.is_newsletter(message, headers, body_snippet)
            
            if is_newsletter:
                # Extract sender info
                sender_info = detector.extract_sender_info(from_header)
                sender_key = sender_info['email']
                
                # Store message info grouped by sender
                senders_map[sender_key]['sender_info'] = sender_info
                senders_map[sender_key]['messages'].append(message)
                senders_map[sender_key]['message_ids'].append(msg['id'])
                senders_map[sender_key]['subjects'].append(subject)
                senders_map[sender_key]['confidence'] = max(
                    senders_map[sender_key].get('confidence', 0),
                    confidence
                )
                
                # Extract unsubscribe info (use first message from sender)
                if 'unsubscribe_info' not in senders_map[sender_key]:
                    unsub_info = extractor.extract(headers, body)
                    senders_map[sender_key]['unsubscribe_info'] = unsub_info
        
        print(f"  ✓ Completed analysis of {len(messages)} messages\n")
        
        # Prepare sender list for review
        senders_list = []
        for email, data in senders_map.items():
            sender_info = data['sender_info']
            unsub_info = data['unsubscribe_info']
            
            senders_list.append({
                'email': email,
                'display_name': sender_info['display_name'],
                'domain': sender_info['domain'],
                'messages_count': len(data['messages']),
                'message_ids': data['message_ids'],
                'sample_subject': data['subjects'][0] if data['subjects'] else '',
                'unsubscribe_type': unsub_info['unsubscribe_type'],
                'unsubscribe_url': unsub_info.get('url'),
                'confidence': data['confidence']
            })
        
        # Sort by message count (most frequent first)
        senders_list.sort(key=lambda x: x['messages_count'], reverse=True)
        
        print(f"Found {len(senders_list)} unique newsletter senders.\n")
        
        if not senders_list:
            print("No newsletters detected. Exiting.")
            return
        
        # Phase 4: Interactive review or auto-approve
        if args.auto_approve:
            print("Phase 4: Auto-approving all newsletters...")
            review_results = {
                'approved': senders_list,
                'skipped': [],
                'kept': []
            }
            print(f"  ✓ Auto-approved {len(senders_list)} senders\n")
        else:
            print("Phase 4: Interactive review...")
            reviewer = InteractiveReviewer()
            review_results = reviewer.review_senders(senders_list)
        
        approved = review_results['approved']
        skipped = review_results['skipped']
        kept = review_results['kept']
        
        # Final confirmation
        if not reviewer.confirm_execution(len(approved)):
            print("Unsubscribe cancelled by user.")
            return
        
        # Phase 5: Execute unsubscribes
        print("\nPhase 5: Executing unsubscribe actions...")
        executor = UnsubscribeExecutor(gmail_client)
        
        execution_results = []
        for i, sender in enumerate(approved, 1):
            print(f"\n[{i}/{len(approved)}] Unsubscribing from {sender['display_name']}...")
            
            result = executor.execute(sender)
            execution_results.append({
                'sender': sender,
                'result': result
            })
            
            print(f"  {result['message']}")
            
            # Label processed messages if enabled
            if AUTO_LABEL_PROCESSED and result['success']:
                for msg_id in sender['message_ids']:
                    gmail_client.add_label(msg_id, LABEL_NAME)
        
        # Phase 6: Generate report
        print("\nPhase 6: Generating summary report...")
        report_gen = ReportGenerator()
        
        stats = {
            'total_scanned': len(messages),
            'senders_detected': len(senders_list),
            'approved': len(approved),
            'skipped': len(skipped),
            'kept': len(kept)
        }
        
        report_gen.generate_summary(stats, execution_results)
        report_gen.print_console_summary(stats, execution_results)
        
        print("✓ All done! Check the summary report for details.\n")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
