"""This sample script demonstrates how to invoke the Sequential Data Store REST API"""

import inspect
import json
import jsonpatch
import math
import traceback

from ocs_sample_library_preview import (SdsType, SdsTypeCode, SdsTypeProperty,
                                        EDSClient, OCSClient, SdsStream, SdsBoundaryType,
                                        SdsStreamPropertyOverride,
                                        SdsStreamViewProperty, SdsStreamView,
                                        SdsStreamIndex, SdsInterpolationMode, Role)

from wave_data import (WaveData, WaveDataCompound, WaveDataInteger,
                       WaveDataTarget)


def get_appsettings():
    """Open and parse the appsettings.json file"""

    # Try to open the configuration file
    try:
        with open(
            'appsettings.json',
            'r',
        ) as f:
            appsettings = json.load(f)
    except Exception as error:
        print(f'Error: {str(error)}')
        print(f'Could not open/read appsettings.json')
        exit()

    return appsettings


def get_wave_data_type(sample_type_id):
    """Creates an SDS type definition for WaveData"""
    if sample_type_id is None or not isinstance(sample_type_id, str):
        raise TypeError('sampleTypeId is not an instantiated string')

    int_type = SdsType('intType', SdsTypeCode.Int32)
    double_type = SdsType('doubleType', SdsTypeCode.Double)

    # note that the Order is the key (primary index)
    order_property = SdsTypeProperty('Order', True, int_type)
    tau_property = SdsTypeProperty('Tau', False, double_type)
    radians_property = SdsTypeProperty('Radians', False, double_type)
    sin_property = SdsTypeProperty('Sin', False, double_type)
    cos_property = SdsTypeProperty('Cos', False, double_type)
    tan_property = SdsTypeProperty('Tan', False, double_type)
    sinh_property = SdsTypeProperty('Sinh', False, double_type)
    cosh_property = SdsTypeProperty('Cosh', False, double_type)
    tanh_property = SdsTypeProperty('Tanh', False, double_type)

    # create an SdsType for WaveData Class
    wave = SdsType(sample_type_id, SdsTypeCode.Object,
                   [order_property, tau_property, radians_property, sin_property, cos_property,
                    tan_property, sinh_property, cosh_property, tanh_property],
                   'WaveDataSample', 'This is a sample Sds type for storing WaveData type events.')
    return wave


def get_wave_compound_data_type(sample_type_id):
    """Creates a compound SDS type definition for WaveData"""
    if sample_type_id is None or not isinstance(sample_type_id, str):
        raise TypeError('sampleTypeId is not an instantiated string')

    int_type = SdsType('intType', SdsTypeCode.Int32)
    double_type = SdsType('doubleType', SdsTypeCode.Double)

    # note that the Order is the key (primary index)
    order_property = SdsTypeProperty('Order', True, int_type, order=1)
    multiplier_property = SdsTypeProperty(
        'Multiplier', True, int_type, order=2)
    tau_property = SdsTypeProperty('Tau', False, double_type)
    radians_property = SdsTypeProperty('Radians', False, double_type)
    sin_property = SdsTypeProperty('Sin', False, double_type)
    cos_property = SdsTypeProperty('Cos', False, double_type)
    tan_property = SdsTypeProperty('Tan', False, double_type)
    sinh_property = SdsTypeProperty('Sinh', False, double_type)
    cosh_property = SdsTypeProperty('Cosh', False, double_type)
    tanh_property = SdsTypeProperty('Tanh', False, double_type)

    # create an SdsType for WaveData Class
    wave = SdsType(sample_type_id, SdsTypeCode.Object,
                   [order_property, multiplier_property, tau_property, radians_property,
                    sin_property, cos_property, tan_property, sinh_property, cosh_property,
                    tanh_property], 'WaveDataTypeCompound',
                   'This is a sample Sds type for storing WaveData type events')

    return wave


def get_wave_data_target_type(sample_type_id):
    """Creates an SDS type definition for WaveDataTarget"""
    if sample_type_id is None or not isinstance(sample_type_id, str):
        raise TypeError('sampleTypeId is not an instantiated string')

    int_type = SdsType('intType', SdsTypeCode.Int32)
    double_type = SdsType('doubleType', SdsTypeCode.Double)

    # note that the Order is the key (primary index)
    order_target_property = SdsTypeProperty('OrderTarget', True, int_type)
    tau_target_property = SdsTypeProperty('TauTarget', False, double_type)
    radians_target_property = SdsTypeProperty(
        'RadiansTarget', False, double_type)
    sin_target_property = SdsTypeProperty('SinTarget', False, double_type)
    cos_target_property = SdsTypeProperty('CosTarget', False, double_type)
    tan_target_property = SdsTypeProperty('TanTarget', False, double_type)
    sinh_target_property = SdsTypeProperty('SinhTarget', False, double_type)
    cosh_target_property = SdsTypeProperty('CoshTarget', False, double_type)
    tanh_target_property = SdsTypeProperty('TanhTarget', False, double_type)

    # create an SdsType for WaveData Class
    wave = SdsType(SAMPLE_TARGET_TYPE_ID, SdsTypeCode.Object,
                   [order_target_property, tau_target_property, radians_target_property,
                    sin_target_property, cos_target_property, tan_target_property,
                    sinh_target_property, cosh_target_property, tanh_target_property],
                   'WaveDataTargetSample',
                   'This is a sample Sds type for storing WaveDataTarget type events')

    return wave


def get_wave_data_integer_type(sample_type_id):
    """Creates an SDS type definition for WaveDataInteger"""
    if sample_type_id is None or not isinstance(sample_type_id, str):
        raise TypeError('sampleTypeId is not an instantiated string')

    int_type = SdsType('intType', SdsTypeCode.Int32)

    # note that the Order is the key (primary index)
    order_target_property = SdsTypeProperty('OrderTarget', True, int_type)
    sin_int_property = SdsTypeProperty('SinInt', False, int_type)
    cos_int_property = SdsTypeProperty('CosInt', False, int_type)
    tan_int_property = SdsTypeProperty('TanInt', False, int_type)

    # create an SdsType for the WaveDataInteger Class
    wave = SdsType(SAMPLE_INTEGER_TYPE_ID, SdsTypeCode.Object,
                   [order_target_property, sin_int_property,
                       cos_int_property, tan_int_property],
                   'WaveDataIntegerSample',
                   'This is a sample Sds type for storing WaveDataInteger type events')

    return wave


def next_wave(order, multiplier):
    """Creates a new WaveData event"""
    radians = (order) * math.pi/32

    new_wave = WaveDataCompound()
    new_wave.order = order
    new_wave.multiplier = multiplier
    new_wave.radians = radians
    new_wave.tau = radians / (2 * math.pi)
    new_wave.sin = multiplier * math.sin(radians)
    new_wave.cos = multiplier * math.cos(radians)
    new_wave.tan = multiplier * math.tan(radians)
    new_wave.sinh = multiplier * math.sinh(radians)
    new_wave.cosh = multiplier * math.cosh(radians)
    new_wave.tanh = multiplier * math.tanh(radians)

    return new_wave


def suppress_error(sds_call):
    """Suppress an error thrown by SDS"""
    try:
        sds_call()
    except Exception as error:
        print(f'Encountered Error: {error}')


def is_prop(value):
    """Check whether a field is a property of an object"""
    return isinstance(value, property)


def to_string(event):
    """Converts an event into a string"""
    string = ''
    props = inspect.getmembers(type(event), is_prop)
    print_order = [2, 3, 4, 0, 6, 5, 1, 7, 8]
    ordered_props = [props[i] for i in print_order]
    for prop in ordered_props:
        value = prop[1].fget(event)
        if value is None:
            string += f'{prop[0]}: , '
        else:
            string += f'{prop[0]}: {value}, '
    return string[:-2]


def to_wave_data(json_obj):
    """Converts JSON object into WaveData type"""
    # Many JSON implementations leave default values out.  We compensate for
    # WaveData, knowing  that all values should be filled in
    wave = WaveData()
    properties = inspect.getmembers(type(wave), is_prop)
    for prop in properties:
        # Pre-Assign the default
        prop[1].fset(wave, 0)

        if prop[0] in json_obj:
            value = json_obj[prop[0]]
            if value is not None:
                prop[1].fset(wave, value)
    return wave


# Sample Data Information
SAMPLE_TYPE_ID = 'WaveData_SampleType'
SAMPLE_TARGET_TYPE_ID = 'WaveDataTarget_SampleType'
SAMPLE_INTEGER_TYPE_ID = 'WaveData_IntegerType'
SAMPLE_STREAM_ID = 'WaveData_SampleStream'
SAMPLE_STREAM_VIEW_ID = 'WaveData_SampleStreamView'
SAMPLE_STREAM_VIEW_INT_ID = 'WaveData_SampleIntStreamView'
STREAM_ID_SECONDARY = 'SampleStream_Secondary'
STREAM_ID_COMPOUND = 'SampleStream_Compound'
COMPOUND_TYPE_ID = 'SampleType_Compound'


def main(test=False):
    """This function is the main body of the SDS sample script"""
    exception = None
    try:
        appsettings = get_appsettings()

        # Step 1
        tenant_id = appsettings.get('TenantId')
        namespace_id = appsettings.get('NamespaceId')
        community_id = appsettings.get('CommunityId')

        if tenant_id == 'default':
            sds_client = EDSClient(
                appsettings.get('ApiVersion'),
                appsettings.get('Resource'))
        else:
            sds_client = OCSClient(
                appsettings.get('ApiVersion'),
                appsettings.get('TenantId'),
                appsettings.get('Resource'),
                appsettings.get('ClientId'),
                appsettings.get('ClientSecret'))

        print(r'------------------------------------------')
        print(r'  _________    .___     __________        ')
        print(r' /   _____/  __| _/_____\______   \___.__.')
        print(r' \_____  \  / __ |/  ___/|     ___<   |  |')
        print(r' /        \/ /_/ |\___ \ |    |    \___  |')
        print(r'/_______  /\____ /____  >|____|    / ____|')
        print(r'        \/      \/    \/           \/     ')
        print(r'------------------------------------------')
        print(f'Sds endpoint at {sds_client.uri}')
        print()

        # Step 2
        #######################################################################
        # SdsType get or creation
        #######################################################################
        print('Creating an SdsType')
        wave_type = get_wave_data_type(SAMPLE_TYPE_ID)
        wave_type = sds_client.Types.getOrCreateType(namespace_id, wave_type)
        assert wave_type.Id == SAMPLE_TYPE_ID, 'Error getting back wave Type'

        # Step 3
        #######################################################################
        # Sds Stream creation
        #######################################################################
        print('Creating an SdsStream')
        stream = SdsStream(SAMPLE_STREAM_ID, wave_type.Id,
                           'WaveStreamPySample', 'A Stream to store the WaveData events')
        sds_client.Streams.createOrUpdateStream(namespace_id, stream)

        # Step 4
        #######################################################################
        # CRUD operations for events
        #######################################################################

        print('Inserting data')
        # Insert a single event
        event = next_wave(0, 2.0)
        sds_client.Streams.insertValues(namespace_id, stream.Id, [event])

        # Insert a list of events
        waves = []
        for error in range(2, 20, 2):
            waves.append(next_wave(error, 2.0))
        sds_client.Streams.insertValues(namespace_id, stream.Id, waves)

        # Step 5
        # Get the last inserted event in a stream
        print('Getting latest event')
        wave = sds_client.Streams.getLastValue(
            namespace_id, stream.Id, WaveData)
        print(to_string(wave))
        print()

        # Get all the events
        waves = sds_client.Streams.getWindowValues(
            namespace_id, stream.Id, WaveData, 0, 180)
        print('Getting all events')
        print(f'Total events found: {str(len(waves))}')
        for wave in waves:
            print(to_string(wave))
        print()

        # Step 6
        # get all values with headers
        waves = sds_client.Streams.getWindowValuesForm(
            namespace_id, stream.Id, None, 0, 180, 'tableh')
        print('Getting all events in table format')
        print(waves)

        # Step 7
        print('Updating events')
        # Update the first event
        event = next_wave(0, 4.0)
        sds_client.Streams.updateValues(namespace_id, stream.Id, [event])

        # Update the rest of the events, adding events that have no prior
        # index entry
        updated_events = []
        for error in range(2, 40, 2):
            event = next_wave(error, 4.0)
            updated_events.append(event)
        sds_client.Streams.updateValues(
            namespace_id, stream.Id, updated_events)

        # Get all the events
        waves = sds_client.Streams.getWindowValues(namespace_id, stream.Id,
                                                   WaveData, 0, 40)
        print('Getting updated events')
        print(f'Total events found: {str(len(waves))}')
        for wave in waves:
            print(to_string(wave))
        print()

        # Step 8
        print('Replacing events')
        # replace one value
        event = next_wave(0, 5.0)
        sds_client.Streams.replaceValues(namespace_id, stream.Id, [event])

        # replace multiple values
        replaced_events = []
        for error in range(2, 40, 2):
            event = next_wave(error, 5.0)
            replaced_events.append(event)
        sds_client.Streams.replaceValues(
            namespace_id, stream.Id, replaced_events)

        # Step 9
        # Get all the events
        waves = sds_client.Streams.getWindowValues(namespace_id, stream.Id,
                                                   WaveData, 0, 180)
        print('Getting replaced events')
        print(f'Total events found: {str(len(waves))}')
        for wave in waves:
            print(to_string(wave))
        print()

        retrieved_interpolated = sds_client.Streams.getRangeValuesInterpolated(
            namespace_id, stream.Id, None, '5', '32', 4)
        print('Sds can interpolate or extrapolate data at an index location '
              'where data does not explicitly exist:')
        print(retrieved_interpolated)
        print()

        # Step 10
        # Filtering from all values
        print('Getting filtered events')
        filtered_events = sds_client.Streams.getWindowValues(
            namespace_id, SAMPLE_STREAM_ID, WaveData, 0, 50, 'Radians lt 3')

        print(f'Total events found: {str(len(filtered_events))}')
        for wave in filtered_events:
            print(to_string(wave))
        print()

        # Step 11
        # Sampling from all values
        print('Getting sampled values')
        sampled_waves = sds_client.Streams.getSampledValues(
            namespace_id, stream.Id, WaveData, 0, 40, 'sin', 4)

        print(f'Total events found: {str(len(sampled_waves))}')
        for wave in sampled_waves:
            print(to_string(wave))
        print()

        # Step 12
        #######################################################################
        # Property Overrides
        #######################################################################

        print('Property Overrides')
        print('Sds can interpolate or extrapolate data at an index location '
              'where data does not explicitly exist:')
        print()

        # We will retrieve three events using the default behavior, Continuous
        waves = sds_client.Streams.getRangeValues(
            namespace_id, stream.Id, WaveData, '1', 0, 3, False,
            SdsBoundaryType.ExactOrCalculated)

        print('Default (Continuous) requesting data starting at index location '
              '"1", where we have not entered data, Sds will interpolate a '
              'value for each property:')

        for wave in waves:
            print(
                f'Order: {wave.order}: Radians: {wave.radians} Cos: {wave.cos}')

        # Create a Discrete stream PropertyOverride indicating that we do not
        #  want Sds to calculate a value for Radians and update our stream
        property_override = SdsStreamPropertyOverride(
            'Radians', interpolation_mode=SdsInterpolationMode.Discrete)

        # update the stream
        props = [property_override]
        stream.PropertyOverrides = props
        sds_client.Streams.createOrUpdateStream(namespace_id, stream)

        waves = sds_client.Streams.getRangeValues(
            namespace_id, stream.Id, WaveData, '1', 0, 3, False,
            SdsBoundaryType.ExactOrCalculated)
        print()
        print('We can override this read behavior on a property by property '
              'basis, here we override the Radians property instructing Sds '
              'not to interpolate.')
        print('Sds will now return the default value for the data type:')
        for wave in waves:
            print(
                f'Order: {wave.order}: Radians: {wave.radians} Cos: {wave.cos}')

        # Step 13
        #######################################################################
        # Stream Views
        #######################################################################

        # Create additional types to define our targets
        wave_target_type = get_wave_data_target_type(SAMPLE_TARGET_TYPE_ID)
        wave_target_type = sds_client.Types.getOrCreateType(namespace_id,
                                                            wave_target_type)

        wave_integer_type = get_wave_data_integer_type(SAMPLE_INTEGER_TYPE_ID)
        wave_integer_type = sds_client.Types.getOrCreateType(namespace_id,
                                                             wave_integer_type)

        # Create an SdsStreamViewProperty objects when we want to explicitly
        # map one property to another
        vp1 = SdsStreamViewProperty('Order', 'OrderTarget')
        vp2 = SdsStreamViewProperty('Sin', 'SinInt')
        vp3 = SdsStreamViewProperty('Cos', 'CosInt')
        vp4 = SdsStreamViewProperty('Tan', 'TanInt')

        # Create a streamView mapping our original type to our target type,
        # data shape is the same so let Sds handle the mapping
        stream_view = SdsStreamView(
            SAMPLE_STREAM_VIEW_ID, wave_type.Id, wave_target_type.Id, 'SampleStreamView')

        # Data shape and data types are different so include explicit mappings
        # between properties
        manual_stream_view = SdsStreamView(SAMPLE_STREAM_VIEW_INT_ID, wave_type.Id,
                                           wave_integer_type.Id, 'SampleIntStreamView',
                                           properties=[vp1, vp2, vp3, vp4])

        automatic_stream_view = sds_client.StreamViews.getOrCreateStreamView(
            namespace_id, stream_view)
        manual_stream_view = sds_client.StreamViews.getOrCreateStreamView(
            namespace_id, manual_stream_view)

        stream_view_map_1 = sds_client.StreamViews.getStreamViewMap(
            namespace_id, automatic_stream_view.Id)

        stream_view_map_2 = sds_client.StreamViews.getStreamViewMap(
            namespace_id, manual_stream_view.Id)

        range_waves = sds_client.Streams.getRangeValues(
            namespace_id, stream.Id, WaveData, '1', 0, 3, False,
            SdsBoundaryType.ExactOrCalculated)
        print()
        print('SdsStreamViews')
        print('Here is some of our data as it is stored on the server:')
        for way in range_waves:
            print(f'Sin: {way.sin}, Cos: {way.cos}, Tan: {way.tan}')

        # StreamView data when retrieved with a streamView
        range_waves = sds_client.Streams.getRangeValues(
            namespace_id, stream.Id, WaveDataTarget, '1', 0, 3, False,
            SdsBoundaryType.ExactOrCalculated, stream_view_id=automatic_stream_view.Id)
        print()
        print('Specifying a streamView with an SdsType of the same shape '
              'returns values that are automatically mapped to the target '
              'SdsType\'s properties: ')
        for way in range_waves:
            print(f'SinTarget: {way.sin_target}, CosTarget: {way.cos_target}, '
                  f'TanTarget: {way.tan_target}')

        range_waves = sds_client.Streams.getRangeValues(
            namespace_id, stream.Id, WaveDataInteger, '1', 0, 3, False,
            SdsBoundaryType.ExactOrCalculated, stream_view_id=manual_stream_view.Id)
        print()
        print('SdsStreamViews can also convert certain types of data, here we '
              'return integers where the original values were doubles:')
        for way in range_waves:
            print(
                f'SinInt: {way.sin_int}, CosInt: {way.cos_int}, TanInt: {way.tan_int}')

        print()
        print('We can query Sds to return the SdsStreamViewMap for our '
              'SdsStreamView, here is the one generated automatically:')
        for prop in stream_view_map_1.Properties:
            print(f'{prop.SourceId} => {prop.TargetId}')

        print()
        print('Here is our explicit mapping, note SdsStreamViewMap will return '
              'all properties of the Source Type, even those without a '
              'corresponding Target property:')
        for prop in stream_view_map_2.Properties:
            if hasattr(prop, 'TargetId'):
                print(f'{prop.SourceId} => {prop.TargetId}')
            else:
                print(f'{prop.SourceId} => Not mapped')

        # Step 14
        print('We will now update the stream type based on the streamview')

        first_val = sds_client.Streams.getFirstValue(namespace_id, stream.Id,
                                                     None)
        sds_client.Streams.updateStreamType(namespace_id, stream.Id,
                                            SAMPLE_STREAM_VIEW_ID)

        new_stream = sds_client.Streams.getStream(
            namespace_id, SAMPLE_STREAM_ID)
        first_val_updated = sds_client.Streams.getFirstValue(namespace_id,
                                                             SAMPLE_STREAM_ID, None)

        print(
            f'The new type id {new_stream.TypeId} compared to the original one '
            f'{stream.TypeId}')
        print(
            f'The new type value {str(first_val)} compared to the original one '
            f'{str(first_val_updated)}')

        # Step 15
        types = sds_client.Types.getTypes(namespace_id, 0, 100)
        types_query = sds_client.Types.getTypes(
            namespace_id, 0, 100, 'Id:*Target*')

        print()
        print('All Types: ')
        for type_i in types:
            print(type_i.Id)

        print('Types after Query: ')
        for type_i in types_query:
            print(type_i.Id)

        if tenant_id != 'default':
            # Step 16
            #######################################################################
            # Tags and Metadata (OCS ONLY)
            #######################################################################
            print()
            print('Let\'s add some Tags and Metadata to our stream:')

            tags = ['waves', 'periodic', '2018', 'validated']
            metadata = {'Region': 'North America', 'Country': 'Canada',
                        'Province': 'Quebec'}

            sds_client.Streams.createOrUpdateTags(
                namespace_id, stream.Id, tags)
            sds_client.Streams.createOrUpdateMetadata(namespace_id, stream.Id,
                                                      metadata)

            print()
            print('Tags now associated with ', stream.Id)
            print(sds_client.Streams.getTags(namespace_id, stream.Id))

            region = sds_client.Streams.getMetadata(
                namespace_id, stream.Id, 'Region')
            country = sds_client.Streams.getMetadata(
                namespace_id, stream.Id, 'Country')
            province = sds_client.Streams.getMetadata(
                namespace_id, stream.Id, 'Province')

            print()
            print('Metadata now associated with', stream.Id, ':')
            print('Metadata key Region: ', region)
            print('Metadata key Country: ', country)
            print('Metadata key Province: ', province)
            print()

            # Step 17
            #######################################################################
            # Update Metadata (OCS ONLY)
            #######################################################################
            print()
            print('Let\'s update the Metadata on our stream:')

            patch = [
                {'op': 'remove', 'path': '/Region'},
                {'op': 'replace', 'path': '/Province', 'value': 'Ontario'},
                {'op': 'add', 'path': '/City', 'value': 'Toronto'}
            ]

            sds_client.Streams.patchMetadata(namespace_id, stream.Id,
                                             patch)

            country = sds_client.Streams.getMetadata(
                namespace_id, stream.Id, 'Country')
            province = sds_client.Streams.getMetadata(
                namespace_id, stream.Id, 'Province')
            city = sds_client.Streams.getMetadata(
                namespace_id, stream.Id, 'City')

            print()
            print('Metadata now associated with', stream.Id, ':')
            print('Metadata key Country: ', country)
            print('Metadata key Province: ', province)
            print('Metadata key City: ', city)
            print()

        #######################################################################
        # Community steps
        #######################################################################
        if (community_id):
            # Step 18
            print()
            print('Get tenant roles')
            roles = sds_client.Roles.getRoles()
            role: Role = None
            for r in roles:
                if r.RoleTypeId == sds_client.Roles.CommunityMemberRoleTypeId and r.CommunityId == community_id:
                    role = r
                    break
            print('Community member Id:')
            print(role.Id)

            print()
            print('Sharing stream to community')
            patch = jsonpatch.JsonPatch(
                [{
                    'op': 'add', 'path': '/RoleTrusteeAccessControlEntries/-',
                    'value': {
                        'AccessRights': 1, 'AccessType': 0,
                        'Trustee': {'ObjectId': role.Id, 'TenantId': None, 'Type': 'Role'}
                    }
                }])
            sds_client.Streams.patchAccessControl(
                namespace_id, SAMPLE_STREAM_ID, patch)

            # Step 19
            print()
            print('Searching the community')
            community_streams = sds_client.Communities.getCommunityStreams(
                community_id, SAMPLE_STREAM_ID)
            print('Found matching streams:')
            for s in community_streams:
                print(s.Id)

            # Step 20
            print()
            print('Getting stream data from the community stream')
            community_stream = community_streams[0]
            community_data = sds_client.Streams.getLastValueUrl(
                community_stream.Self, WaveData)
            print('Retrieved last value:')
            print(community_data.toJson())

        # Step 21
        #######################################################################
        # Delete events
        #######################################################################
        print()
        print('Deleting values from the SdsStream')
        # remove a single value from the stream
        sds_client.Streams.removeValue(namespace_id, stream.Id, 0)

        # remove multiple values from the stream
        sds_client.Streams.removeWindowValues(namespace_id, stream.Id, 0, 40)
        try:
            event = sds_client.Streams.getLastValue(namespace_id, stream.Id,
                                                    WaveData)
            if event is not None:
                raise ValueError
        except TypeError:
            pass
        print('All values deleted successfully!')

        # Step 22
        print('Adding a stream with a secondary index.')
        index = SdsStreamIndex('Radians')
        secondary = SdsStream(STREAM_ID_SECONDARY,
                              SAMPLE_TYPE_ID, indexes=[index])
        secondary = sds_client.Streams.getOrCreateStream(
            namespace_id, secondary)
        count = 0
        if stream.Indexes:
            count = len(stream.Indexes)

        print(
            f'Secondary indexes on streams original: {str(count)}.'
            f'New one: {str(len(secondary.Indexes))}')
        print()

        # Modifying an existing stream with a secondary index.
        print('Modifying a stream to have a secondary index.')

        sample_stream = sds_client.Streams.getStream(
            namespace_id, SAMPLE_STREAM_ID)

        index = SdsStreamIndex('RadiansTarget')
        sample_stream.Indexes = [index]
        sds_client.Streams.createOrUpdateStream(namespace_id, sample_stream)

        sample_stream = sds_client.Streams.getStream(
            namespace_id, SAMPLE_STREAM_ID)
        # Modifying an existing stream to remove the secondary index
        print('Removing a secondary index from a stream.')

        secondary.Indexes = []
        sds_client.Streams.createOrUpdateStream(namespace_id, secondary)
        secondary = sds_client.Streams.getStream(namespace_id, secondary.Id)

        original_length = '0'
        if stream.Indexes:
            original_length = str(len(stream.Indexes))

        secondary_length = '0'
        if secondary.Indexes:
            secondary_length = str(len(secondary.Indexes))

        print(
            f'Secondary indexes on streams original: {original_length}. '
            f'New one: {secondary_length}')

        # Step 23
        # Adding Compound Index Type
        print('Creating an SdsType with a compound index')
        type_compound = get_wave_compound_data_type(COMPOUND_TYPE_ID)
        sds_client.Types.getOrCreateType(namespace_id, type_compound)

        # create an SdsStream
        print('Creating an SdsStream off of type with compound index')
        stream_compound = SdsStream(STREAM_ID_COMPOUND, type_compound.Id)
        sds_client.Streams.createOrUpdateStream(namespace_id, stream_compound)

        # Step 24
        print('Inserting data')
        waves = []
        waves.append(next_wave(1, 10))
        waves.append(next_wave(2, 2))
        waves.append(next_wave(3, 1))
        waves.append(next_wave(10, 3))
        waves.append(next_wave(10, 8))
        waves.append(next_wave(10, 10))
        sds_client.Streams.insertValues(
            namespace_id, STREAM_ID_COMPOUND, waves)

        latest_compound = sds_client.Streams.getLastValue(
            namespace_id, STREAM_ID_COMPOUND, None)
        first_compound = sds_client.Streams.getFirstValue(
            namespace_id, STREAM_ID_COMPOUND, None)
        window_val = sds_client.Streams.getWindowValues(
            namespace_id, STREAM_ID_COMPOUND, None, '2|1', '10|8')

        print(
            f'First data: {str(first_compound)} Latest data: {str(latest_compound)}')
        print('Window Data:')
        print(str(window_val))

    except Exception as error:
        print((f'Encountered Error: {error}'))
        print()
        traceback.print_exc()
        print()
        exception = error

    finally:
        # Step 25

        #######################################################################
        # SdsType, SdsStream, and SdsStreamView deletion
        #######################################################################
        # Clean up the remaining artifacts
        print('Cleaning up')
        print('Deleting the stream')
        suppress_error(lambda: sds_client.Streams.deleteStream(
            namespace_id, SAMPLE_STREAM_ID))
        suppress_error(lambda: sds_client.Streams.deleteStream(
            namespace_id, STREAM_ID_SECONDARY))
        suppress_error(lambda: sds_client.Streams.deleteStream(
            namespace_id, STREAM_ID_COMPOUND))

        print('Deleting the streamViews')
        suppress_error(lambda: sds_client.Streams.deleteStreamView(
            namespace_id, SAMPLE_STREAM_VIEW_ID))
        suppress_error(lambda: sds_client.Streams.deleteStreamView(
            namespace_id, SAMPLE_STREAM_VIEW_INT_ID))

        print('Deleting the types')
        suppress_error(lambda: sds_client.Types.deleteType(
            namespace_id, SAMPLE_TYPE_ID))
        suppress_error(lambda: sds_client.Types.deleteType(
            namespace_id, SAMPLE_TARGET_TYPE_ID))
        suppress_error(lambda: sds_client.Types.deleteType(
            namespace_id, SAMPLE_INTEGER_TYPE_ID))
        suppress_error(lambda: sds_client.Types.deleteType(
            namespace_id, COMPOUND_TYPE_ID))

        if test and exception is not None:
            raise exception
    print('Complete!')


if __name__ == '__main__':
    main()
