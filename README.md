
# Real-Time Trip Monitoring for Taxi Dispatch System

This project implements a real-time event-driven system to monitor and analyze taxi trip data. It uses Azure services to ingest trip events, analyze them for unusual patterns, and notify operations staff via Microsoft Teams using rich Adaptive Cards.

## 1. System Architecture and Logic App Steps

The core of this solution is an Azure Logic App that orchestrates the entire workflow. It acts as the central nervous system, connecting the event ingestion, analysis, and notification components. The architecture follows a serverless, event-driven pattern.

### Architecture Flow:
- **Event Ingestion**: Trip events are generated and sent to an Azure Event Hub.
- **Trigger**: The Logic App is triggered on a batch of events from the Event Hub.
- **Data Processing**: The Logic App parses the JSON data and sends it to an Azure Function for analysis.
- **Analysis**: The Azure Function processes the trip data and flags any trips with unusual characteristics.
- **Conditional Routing**: The Logic App receives the analysis results, iterates through each trip, and uses conditional logic to determine which notification to send.
- **Notification**: Depending on the analysis, a specific Adaptive Card is posted to a designated Microsoft Teams channel.

### Logic App Workflow Breakdown:
- **When events are available in Event Hub**: This is the trigger for the Logic App. It polls the `taxitripevents` Event Hub every 30 seconds, processing up to 50 events at a time. The `splitOn` property ensures the trigger passes each individual event from the batch to the next step.
- **Parse JSON**: This action takes the raw event data from the Event Hub trigger and parses it into a structured object. It's crucial for the schema to match the incoming data exactly, which includes the `ContentData` and `Properties` wrappers. The schema provided correctly handles this nesting.
- **taxi-trip-analyzer-function-analyze_trip**: The Logic App makes an HTTP POST request to the Azure Function. The entire parsed JSON body from the previous step is sent as the request body. The function then analyzes this batch of trips and returns a new JSON array with the analysis results for each trip.
- **For each**: This loop iterates over the array of trip analysis results returned by the Azure Function. Each iteration of the loop processes a single trip's analysis.
- **Condition**: Inside the loop, the first condition checks if a trip is "interesting" by evaluating `@item()?['isInteresting']` from the function's output.
  - **If true**: The workflow proceeds to a nested condition to check for suspicious activity.
  - **If false**: The workflow posts a "Trip Analyzed - No Issues" Adaptive Card to the Teams channel.
- **Condition_1 (Nested)**: This nested condition was found to have an error. The condition attempted to check if `vendorID` was equal to `2` using an incorrect path `(@body('Parse_JSON')?['ContentData']?['ContentData']?['vendorID'])`. Due to a lockout of the associated Algonquin and Azure accounts, this error could not be fixed. A corrected condition would use `item()?['insights']` to check for `SuspiciousVendorActivity`, but the current workflow remains with the original, erroneous logic. The Logic App attempts to post either an `Interesting Trip Detected` card or a `Suspicious Vendor Activity `card based on this faulty condition.

### Teams Actions:
- **Post Suspicious Vendor Activity card**: Triggered if `isInteresting` is `true` AND the vendor is identified as suspicious.
- **Post Interesting Trip Detected card**: Triggered if `isInteresting` is `true`, but the suspicious vendor condition is `false`.
- **Post Trip Analyzed - No Issues card**: Triggered if `isInteresting` is `false`.

## 2. Azure Function Logic

The Python-based Azure Function (`analyze_trip`) serves as the business logic for the system. It receives a batch of trip data and applies a set of rules to identify and flag unusual patterns.

### Function Logic Breakdown:
- **Input**: The function is an HTTP-triggered function that expects a JSON array of trip data in the request body. It's designed to be robust, handling both a single JSON object or a list of objects.
- **Trip Extraction**: It iterates through each record in the input data. The line `trip = record.get("ContentData", {})` is a key part of the logic, as it safely extracts the core trip details from the Event Hubs' `ContentData` wrapper.
- **Rule-based Analysis**: For each trip, it evaluates the following conditions:
  - `distance > 10`: Flags the trip as a `LongTrip`.
  - `passenger_count > 4`: Flags the trip as a `GroupRide`.
  - `payment == "2"`: Flags the trip as a `CashPayment`.
  - `payment == "2"` and `distance < 1`: Flags the trip as `SuspiciousVendorActivity`.
- **Result Aggregation**: The function compiles a list of all identified insights for each trip.
- **Output**: It returns a JSON array of results. Each item in the array includes the original trip data along with the new analysis fields:
  - `insights`: A list of all flags triggered.
  - `isInteresting`: A boolean that is `true` if any flags were triggered.
  - `summary`: A human-readable summary of the analysis.

The `isInteresting` boolean is particularly important as it allows the Logic App to perform a simple, high-level conditional check, streamlining the workflow. The `insights` array is then used in the Logic App to send the most relevant Adaptive Card.

## 3. Demo

### Watch a demonstration of the real-time trip monitoring system in action.

- [Youtube Link to Demo](https://youtu.be/ToQNDxfRUtA)