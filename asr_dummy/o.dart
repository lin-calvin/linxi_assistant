// This file was generated using the following command and may be overwritten.
// dart-dbus generate-remote-object interface.xml

import 'dart:io';
import 'package:dbus/dbus.dart';

/// Signal data for org.agentserver.asr.Active.
class OrgAgentserverAsrActive extends DBusSignal {
  bool get arg_0 => values[0].asBoolean();

  OrgAgentserverAsrActive(DBusSignal signal) : super(sender: signal.sender, path: signal.path, interface: signal.interface, name: signal.name, values: signal.values);
}

/// Signal data for org.agentserver.asr.Input.
class OrgAgentserverAsrInput extends DBusSignal {
  int get arg_0 => values[0].asInt32();

  OrgAgentserverAsrInput(DBusSignal signal) : super(sender: signal.sender, path: signal.path, interface: signal.interface, name: signal.name, values: signal.values);
}

class OrgAgentserverAsr extends DBusRemoteObject {
  /// Stream of org.agentserver.asr.Active signals.
  late final Stream<OrgAgentserverAsrActive> active;

  /// Stream of org.agentserver.asr.Input signals.
  late final Stream<OrgAgentserverAsrInput> input;

  OrgAgentserverAsr(DBusClient client, String destination, DBusObjectPath path) : super(client, name: destination, path: path) {
    active = DBusRemoteObjectSignalStream(object: this, interface: 'org.agentserver.asr', name: 'Active', signature: DBusSignature('b')).asBroadcastStream().map((signal) => OrgAgentserverAsrActive(signal));

    input = DBusRemoteObjectSignalStream(object: this, interface: 'org.agentserver.asr', name: 'Input', signature: DBusSignature('i')).asBroadcastStream().map((signal) => OrgAgentserverAsrInput(signal));
  }
}
