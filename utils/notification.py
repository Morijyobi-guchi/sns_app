import logging

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self, email_sender):
        self.email_sender = email_sender
        logger.debug(f"NotificationManager initialized with EmailSender: {email_sender}")
        
    def notify_new_follower(self, user_email, follower_username):
        try:
            logger.debug(f"Sending follow notification:")
            logger.debug(f"To: {user_email}")
            logger.debug(f"From: {self.email_sender.username}")
            logger.debug(f"Follower: {follower_username}")
            
            subject = "新しいフォロワー"
            body = f"""
            {follower_username}さんがあなたをフォローしました。
            プロフィールを確認するにはアプリにログインしてください。
            """
            
            success = self.email_sender.send_email(user_email, subject, body)
            
            if success:
                logger.debug("Follow notification email sent successfully")
            else:
                logger.warning("Follow notification email sending returned False")
                
        except Exception as e:
            logger.error(f"Failed to send follow notification: {e}", exc_info=True)
            raise