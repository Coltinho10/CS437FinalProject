import boto3
import os

def send_notification(message):
    try:
        # Use default credential provider chain
        sns_client = boto3.client('sns', region_name='us-east-1')
        
        response = sns_client.publish(
            TopicArn='arn:aws:sns:us-east-1:693664697262:PlantMonitorAlerts',
            Message=message,
            Subject='Plant Monitor Alert'
        )
        print("Publish Response:", response)
        return response
    except Exception as e:
        import traceback
        print(f"Error sending notification: {str(e)}")
        traceback.print_exc()
        return None

# Test the function
send_notification("Test message from Python script")