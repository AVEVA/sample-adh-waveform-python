# Sequential Data Store Python Sample

**Version:** 1.2.12

[![Build Status](https://dev.azure.com/AVEVA-VSTS/Cloud%20Platform/_apis/build/status%2Fproduct-readiness%2FADH%2FAVEVA.sample-adh-waveform-python?branchName=main)](https://dev.azure.com/AVEVA-VSTS/Cloud%20Platform/_build/latest?definitionId=16152&branchName=main)

## Building a Python client to make REST API calls to the SDS Service

The sample code in this topic demonstrates how to invoke SDS REST APIs using Python. By examining the code, you will see how to establish a connection to SDS, obtain an authorization token, create an SdsNamespace, SdsType, and SdsStream, and how to create, read, update, and delete values in SDS.

The sections that follow provide a brief description of the process from beginning to end.

Developed against Python 3.9.1.

## To Run this Sample

1. Clone the GitHub repository
1. Install required modules: `pip install -r requirements.txt`
1. Open the folder with your favorite IDE
1. Configure the sample using the file [appsettings.placeholder.json](appsettings.placeholder.json). Before editing, rename this file to `appsettings.json`. This repository's `.gitignore` rules should prevent the file from ever being checked in to any fork or branch, to ensure credentials are not compromised.
1. Update `appsettings.json` with the credentials provided by AVEVA
1. Run `program.py`

To Test the sample:

1. Run `python test.py`

or

1. Install pytest `pip install pytest`
1. Run `pytest program.py`

## Establish a Connection

The sample code uses the samples library which uses the `requests` module, which exposes simple methods for specifying request types to a given destination address. This library automatically adds the `Accept-Encoding` header to requests and decompresses encoded responses before returning them to the user, so no special handling is required to support compression. The client calls the requests method by passing a destination URL, payload, and headers. The server's response is stored.

```python
response = requests.post(url, data=payload, headers=client_headers)
```

- _url_ is the service endpoint (for example:
  `https://uswe.datahub.connect.aveva.com`). The connection is used by the `SdsClient` class.

Each call to the SDS REST API consists of an HTTP request along with a specific URL and HTTP method. The URL consists of the server name plus the extension that is specific to the call. Like all REST APIs, the SDS REST API maps HTTP methods to CRUD operations as shown in the following table:

| HTTP Method | CRUD Operation | Content Found In |
| ----------- | -------------- | ---------------- |
| POST        | Create         | message body     |
| GET         | Retrieve       | URL parameters   |
| PUT         | Update         | message body     |
| DELETE      | Delete         | URL parameters   |

## Configure the Sample

Included in the sample is a configuration file with placeholders that need to be replaced with the proper values. They include information for authentication, connecting to the SDS Service, and pointing to a namespace.

### CONNECT data services

The SDS Service is secured using Azure Active Directory. The sample application is an example of a _confidential client_. Confidential clients provide an application ID and secret that are authenticated against the directory. These are referred to as client IDs and client secrets, which are associated with a given tenant. The steps necessary to create a new client ID and secret are described below.

First, log on to the [Data Hub Portal](https://datahub.connect.aveva.com) as a user with the Tenant Admission role, and navigate to the `Clients` page under the `Security` tab, which is situated along the left side of the webpage. Three types of clients may be created; we will use a `client-credentials` client in this sample, but for the complete explanation all of three types consult the [CONNECT data services clients](https://docs.aveva.com/bundle/aveva-data-hub/page/1263323.html) documentation. 

To create a new client, click on the `+ Add Client` button along the top, and select the desired roles for this client. This sample program covers data creation, deletion, and retrieval, so a role or roles with Read, Write, and Delete permissions on the streams collection and individual streams will be necessary. It is encouraged to not use the Tenant Administrator role for a client if possible, but that is an existing role with the necessary permissions for this sample. Tenant Contributor is a role that by default has Read and Write permissions to the necessary collections, so if deletions are not desired, it is recommended to skip those steps in the sample rather than elevating the client in order to follow along.

After naming the client and selecting the role(s), clicking continue lets you generate a secret. Secrets can always be generated or removed later for the client, but the secret itself can only be seen at creation time; naming the secret something meaningful will assist with maintenance of the secrets over time. Provide an expiration date for the secret; if the client is mapped the Tenant Administrator role, it is strongly encouraged to generate a new, fast-expiring secret for each use.

A pop-up will appear with the tenant ID, client ID and client secret. These must replace the corresponding values in the sample's configuration file.

Finally, a valid namespace ID for the tenant must be given. To create a namespace, click on the `Manage` tab then navigate to the `Namespaces` page. At the top the add button will create a new namespace after the required forms are completed. This namespace is now associated with the logged-in tenant and may be used in the sample.

### Edge Data Store

To run this sample against the Edge Data Store, the sample must be run locally on the machine where Edge Data Store is installed. In addition, the same config information must be entered with the exception of the `[Credentials]` section of the file. For a typical or default installation, the values will be:

- `"NamespaceId": "default"`
- `"Resource": "http://localhost:5590"`
- `"TenantId": "default"`
- `"ApiVersion": "v1"`

### Config Schema

The values to be replaced are in `appsettings.json`:

```json
{
  "Resource": "uswe.datahub.connect.aveva.com",
  "ApiVersion": "v1",
  "TenantId": "PLACEHOLDER_REPLACE_WITH_TENANT_ID",
  "NamespaceId": "PLACEHOLDER_REPLACE_WITH_NAMESPACE_ID",
  "CommunityId": null,
  "ClientId": "PLACEHOLDER_REPLACE_WITH_APPLICATION_IDENTIFIER",
  "ClientSecret": "PLACEHOLDER_REPLACE_WITH_APPLICATION_SECRET"
}
```

### Community

If you would like to see an example of basic interactions with an Cds community, enter an existing community id in the `CommunityId` field of the configuration. Make sure to also grant the appropriate "Community Member" role to the Client-Credentials Client used by the sample. If you have not yet created a community, see the [documentation](https://docs.aveva.com/bundle/aveva-data-hub/page/1263169.html) for instructions. Entering a community id will enable three additional steps in the sample.

If you are not using Cds communities, leave the `CommunityId` field blank.

## Obtain an Authentication Token

Within each request to SDS, the headers are provided by a function that is also responsible for refreshing the token. An authentication context is created and a token is acquired from that context.

```python
tokenInformation = requests.post(
tokenEndpoint,
data = {"client_id" : self.clientId,
        "client_secret" : self.clientSecret,
        "grant_type" : "client_credentials"})

token = json.loads(tokenInformation.content)
```

This is handled by the python library

## Acquire an SdsNamespace

In SDS, a namespace provides isolation within a Tenant. Each namespace has its own collection of Streams, Types, and Stream Views. It is not possible to programmatically create or delete a namespace. If you are a new user, be sure to go to the [Data Hub Portal](https://datahub.connect.aveva.com) and create a namespace using your tenant login credentials provided by AVEVA. You must provide the namespace ID of a valid namespace in `appsettings.json` for the sample to function properly.

Each SdsClient is associated with the tenant passed as an argument to the constructor. There is a one-to-one correspondence between them. However, multiple namespaces may be allocated to a single tenant, so you will see that each function in the library takes in a namespace ID as an argument.

## Create an SdsType

To use SDS, you define SdsTypes that describe the kinds of data you want to store in SdsStreams. SdsTypes are the model that define SdsStreams. SdsTypes can define simple atomic types, such as integers, floats, or strings, or they can define complex types by grouping other SdsTypes. For more information about SdsTypes, refer to the [SDS documentation](https://docs.aveva.com/bundle/data-hub/page/developer-guide/sequential-data-store-dev/sds-lp-dev.html).

In the sample code, the SdsType representing WaveData is defined in the `getWaveDataType` method of program.py. WaveData contains properties of integer and double atomic types. The function begins by defining a base SdsType for each atomic type.

```python
intType = SdsType()
intType.Id = "intType"
intType.SdsTypeCode = SdsTypeCode.Int32
```

Next, the WaveData properties are each represented by an SdsTypeProperty. Each SdsType field in SdsTypeProperty is assigned an integer or double SdsType. The WaveData Order property represents the type's key, and its IsKey property is set to true.

```python
orderProperty = SdsTypeProperty()
orderProperty.Id = "Order"
orderProperty.SdsType = intType
orderProperty.IsKey = True
```

The WaveData SdsType is defined as a collection of the SdsTypeProperties.

```python
#create an SdsType for WaveData Class
wave = SdsType()
wave.Id = sampleTypeId
wave.Name = "WaveDataPySample"
wave.Description = "This is a sample SDS type for storing WaveData type events"
wave.SdsTypeCode = SdsTypeCode.Object
wave.Properties = [orderProperty, tauProperty, radiansProperty,
                    sinProperty, cosProperty, tanProperty, sinhProperty,
                    coshProperty, tanhProperty]
```

The WaveData type is created in SDS using the `createType` method.

```python
type = getWaveDataType(sampleTypeId)
type = sdsClient.Types.getOrCreateType(namespaceId, type)
```

All SdsTypes are constructed in a similar manner. Basic SdsTypes form the basis for SdsTypeProperties, which are then assigned to a complex user-defined type. These types can then be used in properties and become part of another SdsType's property list.

## Create an SdsStream

An SdsStream stores an ordered series of events. To create a SdsStream instance, you simply provide an Id, assign it a type, and submit it to the SDS service. The `createStream` method of SdsClient is similar to createType, except that it uses a different URL. Here is how it is called from the main program:

```python
stream = SdsStream()
stream.Id = sampleStreamId
stream.Name = "WaveStreamPySample"
stream.Description = "A stream to store the WaveData events"
stream.TypeId = type.Id
stream = sdsClient.Streams.createOrUpdateStream(namespaceId, stream)
```

The local SdsStream can be created in the SDS service by a POST request as follows:

```python
response = requests.post(
            self.__uri_API + self.__streamViewsPath.format(tenant_id=self.__tenant, namespace_id=namespace_id, streamView_id=streamView.Id),
            data=streamView.toJson(),
            headers=self.__baseClient.sdsHeaders())
```

## Create and Insert Values into the Stream

A single SdsValue is a data point in the stream. An event object cannot be empty and should have at least the key value of the SDS type for the event. Events are passed in JSON format and are serialized before being sent along with a POST request.

When inserting single or multiple values, the payload has to be a collection of events. An event can be created using the following POST request:

```python
sdsClient.Streams.insertValues(namespaceId, stream.Id, [event])
```

That code looks like this:

```python
payload = json.dumps(events)
response = requests.post(
    self.__url + self.__insertValuesPath.format(api_version=self.__apiVersion, tenant_id=self.__tenant, namespace_id=namespace_id, stream_id=stream_id),
    data=payload,
    headers=self.__sdsHeaders())
```

First the event is created locally by populating a newWave event as follows:

```python
def nextWave(order, multiplier):
    radians = (order) * math.pi/32

    newWave = WaveDataCompound()
    newWave.Order = order
    newWave.Multiplier = multiplier
    newWave.Radians = radians
    newWave.Tau = radians / (2 * math.pi)
    newWave.Sin = multiplier * math.sin(radians)
    newWave.Cos = multiplier * math.cos(radians)
    newWave.Tan = multiplier * math.tan(radians)
    newWave.Sinh = multiplier * math.sinh(radians)
    newWave.Cosh = multiplier * math.cosh(radians)
    newWave.Tanh = multiplier * math.tanh(radians)

    return newWave
```

Then use the data service client to submit the event using the insertValues method:

```python
sdsClient.Streams.insertValues(namespaceId, stream.Id, [event])
```

Similarly, we can build a list of objects and insert them in bulk:

```python
waves = []
for i in range(2, 20, 2):
    waves.append(nextWave(i, 2.0))
sdsClient.Streams.insertValues(namespaceId, stream.Id, waves)
```

The SDS REST API provides many more types of data insertion calls beyond those demonstrated in this application. Go to the [SDS documentation](https://docs.aveva.com/bundle/data-hub/page/developer-guide/sequential-data-store-dev/sds-lp-dev.html) for more information on available REST API calls.

## Retrieve Values from a Stream

There are many methods in the SDS REST API that allow the retrieval of events from a stream. Many of the retrieval methods accept indexes, which are passed using the URL. The index values must be capable of conversion to the type of the index assigned in the SdsType. Below are some of the available methods which have been implemented in SdsClient:

### Get Window Values

`getWindowValues` is used for retrieving events over a specific index range. This is the function definition:

```python
def getWindowValues(self, namespace_id, stream_id, value_class, start, end):
```

- _start_ and _end_ (inclusive) represent the indices for the retrieval.
- The namespace ID and stream ID must be provided to the function call.
- A JSON object containing a list of the found values is returned.

The method is called as shown :

```python
waves = client.getWindowValues(namespaceId, stream.Id, WaveData, 0, 40)
```

You can also retrieve the values in the form of a table (in this case with headers). Here is how to use it:

```python
def getWindowValuesForm(self, namespace_id, stream_id, value_class, start, end, form="")
```

- _start_ and _end_ (inclusive) represent the indices for the retrieval.
- The namespace ID and stream ID must be provided to the function call.
- _form_ specifies the organization of a table, the two available formats are table and header table

Here is how it is called:

```python
waves = sdsClient.Streams.getWindowValuesForm(namespaceId, stream.Id, None, 0, 180,"tableh")
```

### Get Range Values

`getRangeValues` is a method in `SdsClient` used for retrieving a specified number of events from a starting index. The starting index is the ID of the `SdsTypeProperty` that corresponds to the key value of the WaveData type. Here is the request:

```python
def getRangeValues(self, namespace_id, stream_id, value_class, start, skip, count, reversed, boundary, streamView_id=""):
```

- **start** is the increment by which the retrieval will happen.
- **count** is how many values you wish to have returned.
- **reversed** is a boolean that when `true` causes the retrieval to work backwards from the starting point.
- **boundary** is a `SdsBoundaryType` value that determines the behavior if the starting index cannot be found. Refer the to the [SDS documentation](https://docs.aveva.com/bundle/data-hub/page/developer-guide/sequential-data-store-dev/sds-lp-dev.html) for more information about SdsBoundaryTypes.

The `getRangeValues` method is called as shown :

```python
waves = sdsClient.Streams.getRangeValues(namespaceId, stream.Id, WaveData, "1", 0, 3, False, SdsBoundaryType.ExactOrCalculated)
```

### Get Sampled Values

For retrieving a representative sample of data between a start and end index. Sampling is driven by a specified property or properties of the stream's Sds Type. Property types that cannot be interpolated do not support sampling requests. Strings are an example of a property that cannot be interpolated. For more information see [Interpolation.](https://docs.aveva.com/bundle/data-hub/page/developer-guide/sequential-data-store-dev/sds-read-data.html?_gl=1*1s6agl*_up*MQ..*_ga*MjgxMTE3OTc5LjE3MjExNDI2NjE.*_ga_2E8P7THCR4*MTcyMTE0MjY2MC4xLjAuMTcyMTE0MjY2MC4wLjAuMA..*_ga_PNW2Q7E2B0*MTcyMTE0MjY2MC4xLjAuMTcyMTE0MjY2MC4wLjAuMA..#interpolation) Here is how to use it:

```python
def getSampledValues(namespace_id, stream_id, value_class, start, end, sample_by, intervals, filter="", stream_view_id=""):
```

- _intervals_ is the number of intervals requested.
- _sample_by_ defines the property or properties to use when sampling.
- _filter_ is an optional expression to filter by.

Note: This method, implemented for example purposes in `SdsClient`, does not include support for SdsBoundaryTypes. For more information about SdsBoundaryTypes and how to implement them with sampling, refer to the [SDS documentation](https://docs.aveva.com/bundle/data-hub/page/developer-guide/sequential-data-store-dev/sds-lp-dev.html)

The method is called as shown :

```python
waves = sdsClient.Streams.getSampledValues(namespaceId, stream.Id, WaveData, 0, 40, "sin", 4)
```

## Updating and Replacing Values

### Updating Values

```python
# update one value
event = nextWave(start, span, 4.0, 0)
sdsClient.Streams.updateValues(namespaceId, stream.Id, [event])
# update multiple values
updatedEvents = []
    for i in range(2, 40, 2):
        event = nextWave(i, 4.0)
        updatedEvents.append(event)
client.updateValues(namespaceId, stream.Id, updatedEvents)
```

If you attempt to update values that do not exist, they will be created. The sample updates the original ten values and then adds another ten values by updating with a collection of twenty values.

### Replacing Values

In contrast to updating, replacing a value only considers existing values and will not insert any new values into the stream. The sample program demonstrates this by replacing all twenty values. The calling conventions are identical to `updateValue` and `updateValues`:

```python
# replace one value
event = nextWave(0, 5.0)
client.replaceValues(namespaceId, stream.Id, [event])
# replace multiple values
replacedEvents = []
for i in range(2, 40, 2):
    event = nextWave(i, 5.0)
    replacedEvents.append(event)
sdsClient.Streams.replaceValues(namespaceId, stream.Id, replacedEvents)
```

## Property Overrides

SDS has the ability to override certain aspects of an SDS Type at the SDS Stream level. Meaning we apply a change to a specific SDS Stream without changing the SDS Type or the read behavior of any other SDS Streams based on that type.

In the sample, the InterpolationMode is overridden to a value of Discrete for the property Radians. Now if a requested index does not correspond to a real value in the stream then `null`, or the default value for the data type, is returned by the SDS Service. The following shows how this is done in the code:

```python
# Create a Discrete stream PropertyOverride indicating that we do
# not want SDS to calculate a value for Radians and update our stream
propertyOverride = SdsStreamPropertyOverride()
propertyOverride.SdsTypePropertyId = 'Radians'
propertyOverride.InterpolationMode = 3

# update the stream
props = [propertyOverride]
stream.PropertyOverrides = props
sdsClient.Streams.createOrUpdateStream(namespaceId, stream)
```

The process consists of two steps. First, the Property Override must be created, then the stream must be updated. Note that the sample retrieves three data points before and after updating the stream to show that it has changed. See the [SDS documentation](https://docs.aveva.com/bundle/data-hub/page/developer-guide/sequential-data-store-dev/sds-lp-dev.html) for more information about SDS Property Overrides.

## SdsStreamViews

An SdsStreamView provides a way to map stream data requests from one data type to another. You can apply an SdsStreamView to any read or GET operation. SdsStreamView is used to specify the mapping between source and target types.

SDS attempts to determine how to map Properties from the source to the destination. When the mapping is straightforward, such as when the properties are in the same position and of the same data type, or when the properties have the same name, SDS will map the properties automatically.

```python
rangeWaves = sdsClient.Streams.getRangeValues(namespaceId, stream.Id, WaveDataTarget, "1", 0, 3, False, SdsBoundaryType.ExactOrCalculated, automaticStreamView.Id)
```

To map a property that is beyond the ability of SDS to map on its own, you should define an SdsStreamViewProperty and add it to the SdsStreamView's Properties collection.

```python
vp2 = SdsStreamViewProperty()
vp2.SourceId = "Sin"
vp2.TargetId = "SinInt"
...
manualStreamView = SdsStreamView()
manualStreamView.Id = sampleStreamViewIntId
manualStreamView.Name = "SampleIntStreamView"
manualStreamView.TargetTypeId = waveIntegerType.Id
manualStreamView.SourceTypeId = waveType.Id
manualStreamView.Properties = [vp1, vp2, vp3, vp4]
```

You can also use a streamview to change a Stream's type.

```python
sdsClient.Streams.updateStreamType(namespaceId, stream.Id, sampleStreamViewId)
```

## SdsStreamViewMap

When an SdsStreamView is added, SDS defines a plan mapping. Plan details are retrieved as an SdsStreamViewMap. The SdsStreamViewMap provides a detailed Property-by-Property definition of the mapping. The SdsStreamViewMap cannot be written, it can only be retrieved from SDS.

```python
streamViewMap2 = sdsClient.Streams.getStreamViewMap(namespaceId, manualStreamView.Id)
```

## Deleting Values from a Stream

There are two methods in the sample that illustrate removing values from a stream of data. The first method deletes only a single value. The second method removes a window of values, much like retrieving a window of values. Removing values depends on the value's key type ID value. If a match is found within the stream, then that value will be removed. Below are the declarations of both functions:

```python
# remove a single value from the stream
def removeValue(self, namespaceId, stream_id, index):
# remove multiple values from the stream
def removeWindowValues(self, namespaceId, stream_id, index):
```

Here is how the methods are used in the sample:

```python
sdsClient.Streams.removeValue(namespaceId, stream.Id, 0)
sdsClient.Streams.removeWindowValues(namespaceId, stream.Id, 0, 40)
```

As when retrieving a window of values, removing a window is inclusive; that is, both values corresponding to Order=0 and Order=40 are removed from the stream.

## Additional Methods

Notice that there are more methods provided in SdsClient than are discussed in this document, including get methods for types, and streams. Each has both a single get method and a multiple get method, which reflect the data retrieval methods covered above. Below are the function declarations:

```python
def getType(self, namespaceId, type_id):
def getTypes(self, namespaceId):
def getStream(self, namespaceId, stream_id):
def getStreams(self, namespaceId, query, skip, count):
```

For a complete list of HTTP request URLs refer to the [SDS documentation](https://docs.aveva.com/bundle/data-hub/page/developer-guide/sequential-data-store-dev/sds-lp-dev.html).

## Cleanup: Deleting Types, Stream Views and Streams

In order for the program to run repeatedly without collisions, the sample performs some cleanup before exiting. Deleting streams, stream views and types can be achieved by a DELETE REST call and passing the corresponding Id. The following calls are made in the sample code.

```python
sdsClient.Streams.deleteStream(namespaceId, sampleStreamId)
sdsClient.Streams.deleteType(namespaceId, sampleTypeId)
sdsClient.Streams.deleteStreamView(namespaceId, sampleStreamViewId)
```

_Note: Types and Stream Views cannot be deleted until any streams referencing them are deleted first. Their references are counted so deletion will fail if any streams still reference them._

---

Automated test uses Python 3.9.1 x64

For the main Cds waveform samples page [ReadMe](https://github.com/AVEVA/AVEVA-Samples-CloudOperations/blob/main/docs/SDS_WAVEFORM.md)  
For the main Cds samples page [ReadMe](https://github.com/AVEVA/AVEVA-Samples-CloudOperations)  
For the main AVEVA samples page [ReadMe](https://github.com/AVEVA/AVEVA-Samples)
