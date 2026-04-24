import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(AthenaApp());
}

class AthenaApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Athena',
      theme: ThemeData(primarySwatch: Colors.red),
      home: SosPage(),
    );
  }
}

class SosPage extends StatefulWidget {
  @override
  _SosPageState createState() => _SosPageState();
}

class _SosPageState extends State<SosPage> {
  String message = '';

  // Função para enviar SOS
  Future<void> sendSos() async {
    final url = Uri.parse('http://127.0.0.1:8000/sos');
    final body = json.encode({
      "user": "Suelma",
      "latitude": 40.7580,
      "longitude": -73.9855,
      "description": "Test alert from Flutter"
    });

    try {
      final response = await http.post(url,
          headers: {"Content-Type": "application/json"}, body: body);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          message = data['status'];
        });
      } else {
        setState(() {
          message = 'Erro ao enviar SOS';
        });
      }
    } catch (e) {
      setState(() {
        message = 'Erro de conexão';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Athena SOS')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: sendSos,
              style: ElevatedButton.styleFrom(
                primary: Colors.red,
                padding: EdgeInsets.symmetric(horizontal: 50, vertical: 50),
                shape: CircleBorder(),
              ),
              child: Icon(Icons.warning, size: 50),
            ),
            SizedBox(height: 20),
            Text(
              message,
              style: TextStyle(fontSize: 20, color: Colors.black),
            ),
          ],
        ),
      ),
    );
  }
}