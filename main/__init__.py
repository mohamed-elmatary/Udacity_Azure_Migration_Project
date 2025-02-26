
import logging
import psycopg2
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime
from azure.functions import ServiceBusMessage

def main(message: ServiceBusMessage):
    try:
        # Log the Service Bus Message as plaintext

        message_body = message.get_body().decode("utf-8")

        logging.info("Message Body: " + message_body)
        notification_id = int(message.get_body().decode('utf-8'))
        logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)
        # TODO: Get connection to database
        conn = psycopg2.connect(user="azureuser", password="Admin714", host="migration-server714.postgres.database.azure.com", port=5432, database="techconfdb")        
        cursor = conn.cursor()

    
        # TODO: Get notification message and subject from database using the notification_id

        cursor.execute('SELECT id, status, message, submitted_date, completed_date, subject FROM public.notification where id = {};'.format(notification_id))
        notifications = cursor.fetchall()

        # Print all rows
        notification = notifications[0]
        body = notification[2]
        notificationSubject = notification[5]
        print("Data row = (%s, %s, %s)" %(str(notification[0]), str(notification[1]), str(notification[2])))

        # TODO: Get attendees email and name
        cursor.execute('SELECT email, first_name FROM public.attendee ORDER BY id ASC')
        attendees = cursor.fetchall()
        # TODO: Loop through each attendee and send an email with a personalized subject
        for row in attendees:
            subject =  '{}: {}'.format(row[1], notificationSubject)
            send_email(row[0] , subject, body)

        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        cursor.execute("UPDATE public.notification SET status = %s , completed_date = %s WHERE id = %s;", ('Notified {} attendees'.format(len(attendees)), datetime.utcnow(), notification[0]))

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        conn.commit()
        cursor.close()
        conn.close()
        # TODO: Close connection


 
def send_email(email, subject, body):
    try:

        message = Mail(
            from_email=os.environ['ADMIN_EMAIL_ADDRESS'],
            to_emails=email,
            subject=subject,
            html_content='<strong>and easy to do anywhere, even with Python</strong>')
        sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
        sg.send(message)
    except Exception as e:
        print(e.message)



        