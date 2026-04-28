import os
from twilio.rest import Client
from dotenv import load_dotenv

def make_test_call():
    # Load environment variables
    load_dotenv()

    # Twilio credentials
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not auth_token:
        print("Error: TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN is missing from .env")
        return

    # Phone numbers
    twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
    customer_number = os.getenv("CUSTOMER_PHONE_NUMBER", os.getenv("TRANSFER_NUMBER"))
    
    if not twilio_number or not customer_number:
        print("Error: TWILIO_PHONE_NUMBER or CUSTOMER_PHONE_NUMBER is missing from .env")
        return

    # Webhook URL
    base_url = os.getenv("BASE_URL")
    if not base_url:
        print("Error: BASE_URL is missing from .env")
        return
        
    webhook_url = f"{base_url}/voice"

    print(f"Initiating call...")
    print(f"From (AI): {twilio_number}")
    print(f"To (Customer): {customer_number}")
    print(f"Using Webhook: {webhook_url}")
    print("-" * 30)

    try:
        # Initialize Twilio Client
        client = Client(account_sid, auth_token)

        # Create Outbound Call
        call = client.calls.create(
            to=customer_number,
            from_=twilio_number,
            url=webhook_url,
            status_callback=f"{base_url}/call-end",
            status_callback_event=["completed"]
        )

        print(f" Call successfully initiated!")
        print(f"Call SID: {call.sid}")
        print("Please answer your phone. The AI Voice Agent will greet you.")

    except Exception as e:
        print(f" Failed to initiate call: {e}")

if __name__ == "__main__":
    make_test_call()
