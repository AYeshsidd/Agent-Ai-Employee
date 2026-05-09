#!/usr/bin/env python3
"""Social Media MCP Module - Handles social media operations"""
from pathlib import Path
from typing import Dict, Any, Optional, List
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mcp_server.modules.base_module import MCPModule
from mcp_server.actions.send_notification import SendNotificationAction


class SocialModule(MCPModule):
    """
    Social Media communication module.

    Provides tools for:
    - LinkedIn posting and messaging
    - Twitter/X posting and messaging  
    - Facebook posting and messaging
    - Notifications
    - Social media scheduling (future)
    """

    def __init__(self):
        self.notification_action = SendNotificationAction()
        self.linkedin_session = None
        self.twitter_session = None
        self.facebook_session = None
        super().__init__("Social")

    def _register_tools(self):
        """Register social media tools"""
        self._tools = {
            "send_notification": {
                "handler": self._send_notification,
                "schema": {
                    "name": "send_notification",
                    "description": "Send a notification (console + log)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Notification title"
                            },
                            "message": {
                                "type": "string",
                                "description": "Notification message"
                            },
                            "priority": {
                                "type": "string",
                                "description": "Notification priority (low, medium, high)",
                                "enum": ["low", "medium", "high"]
                            }
                        },
                        "required": ["title", "message"]
                    }
                }
            },
            "post_to_linkedin": {
                "handler": self._post_to_linkedin,
                "schema": {
                    "name": "post_to_linkedin",
                    "description": "Post content to LinkedIn (requires browser)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Post content (max 3000 characters)"
                            },
                            "post_id": {
                                "type": "string",
                                "description": "Unique identifier for duplicate prevention"
                            }
                        },
                        "required": ["content", "post_id"]
                    }
                }
            },
            "post_to_twitter": {
                "handler": self._post_to_twitter,
                "schema": {
                    "name": "post_to_twitter",
                    "description": "Post a tweet to Twitter/X (max 280 characters)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Tweet content (max 280 characters)"
                            },
                            "post_id": {
                                "type": "string",
                                "description": "Unique identifier for duplicate prevention"
                            }
                        },
                        "required": ["content", "post_id"]
                    }
                }
            },
            "post_to_facebook": {
                "handler": self._post_to_facebook,
                "schema": {
                    "name": "post_to_facebook",
                    "description": "Post content to Facebook",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Post content"
                            },
                            "post_id": {
                                "type": "string",
                                "description": "Unique identifier for duplicate prevention"
                            }
                        },
                        "required": ["content", "post_id"]
                    }
                }
            },
            "auto_post_twitter_from_vault": {
                "handler": self._auto_post_twitter_from_vault,
                "schema": {
                    "name": "auto_post_twitter_from_vault",
                    "description": "Auto-post a Vault task to Twitter",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_filename": {
                                "type": "string",
                                "description": "Task filename in Vault/Needs_Action"
                            }
                        },
                        "required": ["task_filename"]
                    }
                }
            },
            "auto_post_facebook_from_vault": {
                "handler": self._auto_post_facebook_from_vault,
                "schema": {
                    "name": "auto_post_facebook_from_vault",
                    "description": "Auto-post a Vault task to Facebook",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_filename": {
                                "type": "string",
                                "description": "Task filename in Vault/Needs_Action"
                            }
                        },
                        "required": ["task_filename"]
                    }
                }
            },
            "read_twitter_messages": {
                "handler": self._read_twitter_messages,
                "schema": {
                    "name": "read_twitter_messages",
                    "description": "Read recent Twitter/X DMs",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "count": {
                                "type": "number",
                                "description": "Number of messages to read (default: 10)"
                            }
                        }
                    }
                }
            },
            "read_facebook_messages": {
                "handler": self._read_facebook_messages,
                "schema": {
                    "name": "read_facebook_messages",
                    "description": "Read recent Facebook Messenger messages",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "count": {
                                "type": "number",
                                "description": "Number of messages to read (default: 10)"
                            }
                        }
                    }
                }
            },
            "reply_to_twitter_message": {
                "handler": self._reply_to_twitter_message,
                "schema": {
                    "name": "reply_to_twitter_message",
                    "description": "Reply to a Twitter/X DM",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "recipient": {
                                "type": "string",
                                "description": "Username to reply to"
                            },
                            "message": {
                                "type": "string",
                                "description": "Reply message content"
                            }
                        },
                        "required": ["recipient", "message"]
                    }
                }
            },
            "reply_to_facebook_message": {
                "handler": self._reply_to_facebook_message,
                "schema": {
                    "name": "reply_to_facebook_message",
                    "description": "Reply to a Facebook Messenger message",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "recipient": {
                                "type": "string",
                                "description": "Name to reply to"
                            },
                            "message": {
                                "type": "string",
                                "description": "Reply message content"
                            }
                        },
                        "required": ["recipient", "message"]
                    }
                }
            },
            "generate_social_summary": {
                "handler": self._generate_social_summary,
                "schema": {
                    "name": "generate_social_summary",
                    "description": "Generate a summary of social media messages",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "platform": {
                                "type": "string",
                                "description": "Platform to summarize (twitter, facebook, linkedin)",
                                "enum": ["twitter", "facebook", "linkedin"]
                            },
                            "messages": {
                                "type": "array",
                                "items": {"type": "object"},
                                "description": "List of message objects"
                            }
                        },
                        "required": ["platform", "messages"]
                    }
                }
            }
        }

    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute social media tool"""
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(tool_name, parameters)
        if not is_valid:
            return {
                "status": "failed",
                "message": error_msg
            }

        if tool_name not in self._tools:
            return {
                "status": "failed",
                "message": f"Unknown tool: {tool_name}"
            }

        try:
            handler = self._tools[tool_name]["handler"]
            return handler(parameters)
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Social media tool execution failed: {str(e)}"
            }

    def _send_notification(self, params: Dict[str, str]) -> Dict[str, str]:
        """Send notification"""
        return self.notification_action.execute(params)

    def _post_to_linkedin(self, params: Dict[str, str]) -> Dict[str, str]:
        """Post to LinkedIn"""
        content = params.get("content", "")
        post_id = params.get("post_id", "")

        if len(content) > 3000:
            return {
                "status": "failed",
                "message": "Content exceeds 3000 character limit"
            }

        try:
            from skills.linkedin_auto_post_skill import LinkedInAutoPostSkill
            
            if not self.linkedin_session:
                self.linkedin_session = LinkedInAutoPostSkill()
                if not self.linkedin_session.authenticate():
                    return {
                        "status": "failed",
                        "message": "Failed to authenticate with LinkedIn"
                    }

            success = self.linkedin_session.post_to_linkedin(content, post_id)
            
            if success:
                return {
                    "status": "success",
                    "message": f"LinkedIn post created (ID: {post_id})"
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Failed to post to LinkedIn (ID: {post_id})"
                }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"LinkedIn post failed: {str(e)}"
            }

    def _post_to_twitter(self, params: Dict[str, str]) -> Dict[str, str]:
        """Post to Twitter/X"""
        content = params.get("content", "")
        post_id = params.get("post_id", "")

        if len(content) > 280:
            return {
                "status": "failed",
                "message": "Tweet exceeds 280 character limit"
            }

        try:
            from skills.twitter_agent_skill import TwitterAgentSkill
            
            if not self.twitter_session:
                self.twitter_session = TwitterAgentSkill()
                if not self.twitter_session.authenticate():
                    return {
                        "status": "failed",
                        "message": "Failed to authenticate with Twitter"
                    }

            success = self.twitter_session.post_tweet(content, post_id)
            
            if success:
                return {
                    "status": "success",
                    "message": f"Tweet posted successfully (ID: {post_id})"
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Failed to post tweet (ID: {post_id})"
                }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Twitter post failed: {str(e)}"
            }

    def _post_to_facebook(self, params: Dict[str, str]) -> Dict[str, str]:
        """Post to Facebook"""
        content = params.get("content", "")
        post_id = params.get("post_id", "")

        try:
            from skills.facebook_agent_skill import FacebookAgentSkill
            
            if not self.facebook_session:
                self.facebook_session = FacebookAgentSkill()
                if not self.facebook_session.authenticate():
                    return {
                        "status": "failed",
                        "message": "Failed to authenticate with Facebook"
                    }

            success = self.facebook_session.post_to_facebook(content, post_id)
            
            if success:
                return {
                    "status": "success",
                    "message": f"Facebook post created (ID: {post_id})"
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Failed to post to Facebook (ID: {post_id})"
                }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Facebook post failed: {str(e)}"
            }

    def _read_twitter_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read Twitter/X messages"""
        count = params.get("count", 10)

        try:
            from skills.twitter_agent_skill import TwitterAgentSkill
            
            if not self.twitter_session:
                self.twitter_session = TwitterAgentSkill()
                if not self.twitter_session.authenticate():
                    return {
                        "status": "failed",
                        "message": "Failed to authenticate with Twitter"
                    }

            messages = self.twitter_session.read_messages(count)
            
            return {
                "status": "success",
                "message": f"Read {len(messages)} Twitter messages",
                "messages": messages
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Failed to read Twitter messages: {str(e)}"
            }

    def _read_facebook_messages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read Facebook Messenger messages"""
        count = params.get("count", 10)

        try:
            from skills.facebook_agent_skill import FacebookAgentSkill
            
            if not self.facebook_session:
                self.facebook_session = FacebookAgentSkill()
                if not self.facebook_session.authenticate():
                    return {
                        "status": "failed",
                        "message": "Failed to authenticate with Facebook"
                    }

            messages = self.facebook_session.read_messages(count)
            
            return {
                "status": "success",
                "message": f"Read {len(messages)} Facebook messages",
                "messages": messages
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Failed to read Facebook messages: {str(e)}"
            }

    def _reply_to_twitter_message(self, params: Dict[str, str]) -> Dict[str, str]:
        """Reply to Twitter/X message"""
        recipient = params.get("recipient", "")
        message = params.get("message", "")

        try:
            from skills.twitter_agent_skill import TwitterAgentSkill
            
            if not self.twitter_session:
                self.twitter_session = TwitterAgentSkill()
                if not self.twitter_session.authenticate():
                    return {
                        "status": "failed",
                        "message": "Failed to authenticate with Twitter"
                    }

            success = self.twitter_session.reply_to_message(recipient, message)
            
            if success:
                return {
                    "status": "success",
                    "message": f"Reply sent to {recipient}"
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Failed to send reply to {recipient}"
                }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Twitter reply failed: {str(e)}"
            }

    def _reply_to_facebook_message(self, params: Dict[str, str]) -> Dict[str, str]:
        """Reply to Facebook Messenger message"""
        recipient = params.get("recipient", "")
        message = params.get("message", "")

        try:
            from skills.facebook_agent_skill import FacebookAgentSkill
            
            if not self.facebook_session:
                self.facebook_session = FacebookAgentSkill()
                if not self.facebook_session.authenticate():
                    return {
                        "status": "failed",
                        "message": "Failed to authenticate with Facebook"
                    }

            success = self.facebook_session.reply_to_message(recipient, message)
            
            if success:
                return {
                    "status": "success",
                    "message": f"Reply sent to {recipient}"
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Failed to send reply to {recipient}"
                }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Facebook reply failed: {str(e)}"
            }

    def _generate_social_summary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate social media summary"""
        platform = params.get("platform", "")
        messages = params.get("messages", [])

        try:
            if platform == "twitter":
                from skills.twitter_agent_skill import TwitterAgentSkill
                skill = TwitterAgentSkill()
                summary = skill.generate_summary(messages)
            elif platform == "facebook":
                from skills.facebook_agent_skill import FacebookAgentSkill
                skill = FacebookAgentSkill()
                summary = skill.generate_summary(messages)
            else:
                # Generic summary
                summary = f"Social Media Summary\nTotal Messages: {len(messages)}\n"
                for msg in messages[:5]:
                    summary += f"- {msg.get('from', 'Unknown')}: {msg.get('message', '')[:50]}...\n"

            return {
                "status": "success",
                "message": "Summary generated",
                "summary": summary
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Summary generation failed: {str(e)}"
            }

    def _auto_post_twitter_from_vault(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Auto-post a Vault task to Twitter"""
        task_filename = params.get("task_filename", "")

        try:
            from skills.twitter_auto_post_skill import TwitterAutoPostSkill
            from config import Config
            
            skill = TwitterAutoPostSkill()
            
            # Find task in Needs_Action folder
            task_path = Config.NEEDS_ACTION / task_filename
            
            if not task_path.exists():
                return {
                    "status": "failed",
                    "message": f"Task not found: {task_filename}"
                }
            
            success = skill.post_from_vault_task(task_path)
            
            if success:
                return {
                    "status": "success",
                    "message": f"Posted {task_filename} to Twitter"
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Failed to post {task_filename} to Twitter"
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Twitter auto-post failed: {str(e)}"
            }

    def _auto_post_facebook_from_vault(self, params: Dict[str, str]) -> Dict[str, Any]:
        """Auto-post a Vault task to Facebook"""
        task_filename = params.get("task_filename", "")

        try:
            from skills.facebook_auto_post_skill import FacebookAutoPostSkill
            from config import Config
            
            skill = FacebookAutoPostSkill()
            
            # Find task in Needs_Action folder
            task_path = Config.NEEDS_ACTION / task_filename
            
            if not task_path.exists():
                return {
                    "status": "failed",
                    "message": f"Task not found: {task_filename}"
                }
            
            success = skill.post_from_vault_task(task_path)
            
            if success:
                return {
                    "status": "success",
                    "message": f"Posted {task_filename} to Facebook"
                }
            else:
                return {
                    "status": "failed",
                    "message": f"Failed to post {task_filename} to Facebook"
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Facebook auto-post failed: {str(e)}"
            }

    def cleanup(self):
        """Cleanup social module resources"""
        if self.linkedin_session:
            self.linkedin_session.close()
        if self.twitter_session:
            self.twitter_session.close()
        if self.facebook_session:
            self.facebook_session.close()
        super().cleanup()
