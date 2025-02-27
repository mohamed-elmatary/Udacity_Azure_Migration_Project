# TechConf Registration Website

## Project Overview
The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:
 - The web application is not scalable to handle user load at peak
 - When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
 - The current architecture is not cost-effective 

In this project, you are tasked to do the following:
- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:
- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App
1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
      - `POSTGRES_URL`
      - `POSTGRES_USER`
      - `POSTGRES_PW`
      - `POSTGRES_DB`
      - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function
1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

      **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.
      - The Azure Function should do the following:
         - Process the message which is the `notification_id`
         - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
         - Query the database to retrieve a list of attendees (**email** and **first name**)
         - Loop through each attendee and send a personalized subject message
         - After the notification, update the notification status with the total number of attendees notified
2. Publish the Azure Function

### Part 3: Refactor `routes.py`
1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis
Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:

| Azure Resource | Service Tier | Monthly Cost |
| ------------ | ------------ | ------------ |
| * Azure Postgres Database* |  Premium v3 P1V3   |        $34.57      |
| * Azure Service Bus*   |    Basic     |         <$0.01     |
| * 2 Azure App Service Plan *     |     Premium v3 |     $41     |
| * 2 Storage Account *     |     Premium SSD V2 |     $5.72     |
| * Functions *     |     Premium SSD V2 |     $0.0     |



## Architecture Explanation
This is a placeholder section where you can provide an explanation and reasoning for your architecture selection for both the Azure Web App and Azure Function.

- first Azure Web App in current of situation the web app contain Lightweight APIs tend to be well-suited to App Services, and won't approach the size limit for App Services very easily. Additionally, App Services cost less. Lastly, since the ability to scale   quickly is less of a concern, we don't need to factor that into the analysis.
- second Azure Function is a good compute option suitable for our case and we can intgerat easily our Azure Service Bus Queue Trigger function easily with our service bus with help of azure tool in visual studio code 


- current architecture we used Azure Wep App on App Service Plan to avoid any complexity in deployment and management in Azure Virtual Machine, App Service adds the power of Microsoft Azure to your application, including improved security, load balancing, autoscaling, and automated management also support multiple languages and frameworks
because App Service is Paas but virtual machine is Iaas for our web app the app service plan it will be very suitable because our app has lightweight APIs so App Service will be suitable for current and previous architecture

- previous architecture we may face a performance problem like scenario you mentioned (If we are triggering mail through the web app, if there are 1000 attendees the user must wait on the notification page until all attendees are notified due to this timeout issues can easily occur.)
  this could happen because if you send email for each attendee that could take long time and also may fail to send email due to network
  so we solved this issue by modifying architecture by decoupling the specific part of the application that can consume more time and may cause performance issue or timeout and also not adding any thing return to user in response
  this part also can run in background process asynchronously and doesn't affect response this like very small microservices architecture 
  here the role of azure function we moved this part of code to it to process our notification, we also send notification_id to message broker and subscriber (Azure Function will care with this part of sending email and update db)
  if the azure function crashed or didn't consume the message we still have another opportunity due to retry mechanism in the message brocker after fix the crashing

- azure function consider Lightweight APIs 

 * Processing data and data streams
 * Integration with Other Azure Services like serviceBus
 * Supports Different Programming Languages
 * Cost-Efficient

- ServiceBus Azure Service Bus is a fully managed enterprise message broker with queues base on publish-subscribe pattern used to decouple applications and services from each other transferring data between application and service in form of message
  in our case between TECHCONF2022 and Our azure funtion that process notification and send email to all attendees
  azure service bus can integrate with azure function easily


- Azure Postgres Database as it is Fully Managed Service no Infrastructure Management Azure handles the underlying infrastructure, such as hardware, networking, and storage, allowing you to focus on your application and data i think it was very easy to integrate and dealing with it.
  it is first time for me dealing with postgres i always use sql server but i think they are similar and PgAdmin was very friendly and using Sql Query Language is a big feature help me to accomplish task of (connection, query and update DB by psycopg2) very easy  


- Drawbacks ** this architecture like small microservices architecture we have service to save notification and other to process the notification and update db,
  we communicate between them asynchronously during message broker (Azure Service Bus) so now we have two services instead of one and also message broker although the benefit we get from decoupling the appliction and solve problem of performance 
  also problem in one component like azure service doesn't affect other component TechConf2022 app (the application still working) doesn't affect on avilabilty of application
  ** but we increased the complexity of architecture , need more skills and tools to use , more time to build , and also increase complexity of monitoring and troubleshooting and problem detection to know which part has 
  the problem
  increased debugging in multiple apps this consume more time
  also this architecture made me need additional resources from azure to accomplish it this added additional costs for me 
