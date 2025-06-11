import statistics
from typing import List, Dict

from telethon.tl.types import Message


class ManagerPerformanceAnalyzer:
    def __init__(self, messages: List[Message], manager_id: int):
        """
        Initialize analyzer with Telethon Message objects and manager's ID
        
        Args:
            messages: List of Telethon Message objects
            manager_id: Telegram user ID of the manager
        """
        self.messages = messages
        self.manager_id = manager_id

    def analyze(self) -> Dict:
        """Perform comprehensive analysis of manager performance"""
        if not self.messages:
            return {
                'total_messages': 0,
                'metrics': {},
                'summary': "No messages to analyze"
            }

        # Filter out empty messages and classify by role
        valid_messages = [m for m in self.messages if m.message]  # Only messages with text
        manager_messages = [m for m in valid_messages 
                          if m.from_id and hasattr(m.from_id, 'user_id') 
                          and m.from_id.user_id == self.manager_id]
        client_messages = [m for m in valid_messages 
                         if m.from_id and hasattr(m.from_id, 'user_id') 
                         and m.from_id.user_id != self.manager_id]

        # Calculate response times
        response_times = []
        last_client_msg = None
        for msg in valid_messages:
            is_client = (msg.from_id and hasattr(msg.from_id, 'user_id') 
                        and msg.from_id.user_id != self.manager_id)
            is_manager = (msg.from_id and hasattr(msg.from_id, 'user_id') 
                         and msg.from_id.user_id == self.manager_id)
            
            if is_client:
                last_client_msg = msg
            elif is_manager and last_client_msg:
                time_diff = (msg.date - last_client_msg.date).total_seconds() / 60  # in minutes
                if 0 <= time_diff <= 24 * 60:  # Only count responses within 24 hours
                    response_times.append(time_diff)

        # Calculate basic metrics
        metrics = {
            'total_messages': len(valid_messages),
            'manager_messages': len(manager_messages),
            'client_messages': len(client_messages),
            'response_rate': len(manager_messages) / len(client_messages) if client_messages else 0,
            'avg_response_time': statistics.mean(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'initiated_by_manager': 1 if valid_messages and 
                                     valid_messages[0].from_id and 
                                     hasattr(valid_messages[0].from_id, 'user_id') and 
                                     valid_messages[0].from_id.user_id == self.manager_id else 0
        }

        # Calculate working hours response times (9:00 - 18:00)
        working_hours_responses = [
            t for t in response_times
            if 9 <= t.hour < 18 and t.weekday() < 5  # Monday to Friday, 9 AM to 6 PM
        ]

        # Add detailed analysis
        detailed = {
            'quick_responses': len([t for t in response_times if t < 5]),  # responses under 5 minutes
            'slow_responses': len([t for t in response_times if t > 30]),  # responses over 30 minutes
            'messages_per_conversation': metrics['total_messages'],
            'working_hours_avg_response': (
                statistics.mean(working_hours_responses) if working_hours_responses else 0
            ),
            'out_of_hours_messages': sum(
                1 for m in manager_messages
                if m.date.hour < 9 or m.date.hour >= 18 or m.date.weekday() >= 5
            )
        }

        # Generate performance summary
        summary = self._generate_summary(metrics, detailed)

        return {
            'total_messages': metrics['total_messages'],
            'metrics': {**metrics, **detailed},
            'summary': summary
        }

    def _generate_summary(self, metrics: Dict, detailed: Dict) -> str:
        """Generate a human-readable summary of the analysis"""
        response_time_rating = "Excellent" if metrics['avg_response_time'] < 5 else \
                             "Good" if metrics['avg_response_time'] < 15 else \
                             "Fair" if metrics['avg_response_time'] < 30 else "Poor"

        return (
            f"Manager Performance Summary:\n"
            f"- Total Messages: {metrics['total_messages']}\n"
            f"- Response Rate: {metrics['response_rate']:.2f} responses per client message\n"
            f"- Average Response Time: {metrics['avg_response_time']:.1f} minutes ({response_time_rating})\n"
            f"- Working Hours Avg Response: {detailed['working_hours_avg_response']:.1f} minutes\n"
            f"- Quick Responses (<5min): {detailed['quick_responses']}\n"
            f"- Slow Responses (>30min): {detailed['slow_responses']}\n"
            f"- Out of Hours Messages: {detailed['out_of_hours_messages']}\n"
            f"- Conversation Initiative: {'Yes' if metrics['initiated_by_manager'] else 'No'}"
        )