import os
import zipfile

# Define project root and zip file path
project_root = "/mnt/data/ScanAndReadApp_Improved"
zip_path = "/mnt/data/ScanAndReadApp_Improved_with_TTS_and_Save.zip"

# Create necessary directories
os.makedirs(f"{project_root}/lib/screens", exist_ok=True)
os.makedirs(f"{project_root}/lib/services", exist_ok=True)
os.makedirs(f"{project_root}/lib/utils", exist_ok=True)

# Define file contents
main_dart = """
import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const ScanAndReadApp());
}

class ScanAndReadApp extends StatelessWidget {
  const ScanAndReadApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Scan and Read',
      theme: ThemeData(primarySwatch: Colors.teal),
      home: const HomeScreen(),
    );
  }
}
"""

home_screen_dart = """
import 'package:flutter/material.dart';
import '../services/ocr_service.dart';
import 'edit_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  Future<void> scanAndNavigate(BuildContext context) async {
    String scannedText = await OCRService.scanText();
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => EditScreen(text: scannedText)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Scan and Read')),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              "Tip: Use good lighting, keep text flat and centered.",
              style: TextStyle(fontSize: 14, color: Colors.grey.shade700),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () => scanAndNavigate(context),
              child: const Text("Start Scanning"),
            ),
          ],
        ),
      ),
    );
  }
}
"""

edit_screen_dart = """
import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'dart:io';
import 'package:path_provider/path_provider.dart';

class EditScreen extends StatefulWidget {
  final String text;
  const EditScreen({super.key, required this.text});

  @override
  State<EditScreen> createState() => _EditScreenState();
}

class _EditScreenState extends State<EditScreen> {
  late TextEditingController _controller;
  final FlutterTts flutterTts = FlutterTts();

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.text);
  }

  Future<void> _speakText() async {
    await flutterTts.setLanguage("en-US");
    await flutterTts.setPitch(1.0);
    await flutterTts.setSpeechRate(0.5);
    await flutterTts.speak(_controller.text);
  }

  Future<void> _saveTextToFile() async {
    final directory = await getApplicationDocumentsDirectory();
    final file = File('${directory.path}/scanned_text_${DateTime.now().millisecondsSinceEpoch}.txt');
    await file.writeAsString(_controller.text);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text("Document saved to ${file.path}")),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Scanned Text")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Expanded(
              child: TextField(
                controller: _controller,
                maxLines: null,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Edit scanned text here...',
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton.icon(
                  icon: const Icon(Icons.volume_up),
                  label: const Text("Read Aloud"),
                  onPressed: _speakText,
                ),
                ElevatedButton.icon(
                  icon: const Icon(Icons.save),
                  label: const Text("Save"),
                  onPressed: _saveTextToFile,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
"""

ocr_service_dart = """
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';

class OCRService {
  static Future<String> scanText() async {
    final picker = ImagePicker();
    final XFile? pickedFile = await picker.pickImage(source: ImageSource.camera);
    if (pickedFile == null) return 'No image selected.';

    final inputImage = InputImage.fromFile(File(pickedFile.path));
    final textRecognizer = TextRecognizer();
    final RecognizedText recognizedText = await textRecognizer.processImage(inputImage);
    textRecognizer.close();

    return recognizedText.text.isEmpty ? 'No recognizable text found.' : recognizedText.text;
  }
}
"""

# Save files
with open(f"{project_root}/lib/main.dart", "w") as f:
    f.write(main_dart)
with open(f"{project_root}/lib/screens/home_screen.dart", "w") as f:
    f.write(home_screen_dart)
with open(f"{project_root}/lib/screens/edit_screen.dart", "w") as f:
    f.write(edit_screen_dart)
with open(f"{project_root}/lib/services/ocr_service.dart", "w") as f:
    f.write(ocr_service_dart)

# Zip the project directory
with zipfile.ZipFile(zip_path, "w") as zipf:
    for root, dirs, files in os.walk(project_root):
        for file in files:
            filepath = os.path.join(root, file)
            arcname = os.path.relpath(filepath, start=project_root)
            zipf.write(filepath, arcname=arcname)

print(f"Project zipped at: {zip_path}")
