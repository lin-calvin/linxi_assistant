// This file was generated using the following command and may be overwritten.
// dart-dbus generate-remote-object interface.xml

import 'dart:io';
import 'package:dbus/dbus.dart';

class OrgAgentserverAgent extends DBusRemoteObject {
  OrgAgentserverAgent(DBusClient client, String destination, DBusObjectPath path) : super(client, name: destination, path: path);

  /// Invokes org.agentserver.agent.Speech()
  Future<int> callSpeech(String input, {bool noAutoStart = false, bool allowInteractiveAuthorization = false}) async {
    var result = await callMethod('org.agentserver.agent', 'Speech', [DBusString(input)], replySignature: DBusSignature('i'), noAutoStart: noAutoStart, allowInteractiveAuthorization: allowInteractiveAuthorization);
    return result.returnValues[0].asInt32();
  }
}
