const express = require('express');
const multer = require('multer');
const fs = require('fs');
const PDFParser = require('pdf-parse');
const axios = require('axios');

const { PDFLoader } = require("langchain/document_loaders/fs/pdf");

const app = express();
const port = 3000;

const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

app.use(express.static('public'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});


app.post('/parsepdf', upload.single('pdfFile'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No PDF file provided' });
    }


    // const loader = new PDFLoader(req.file.buffer, {splitPages: false,});
    // const data = await loader.load();

    const pdfBuffer = req.file.buffer;
    const data = await PDFParser(pdfBuffer);

    // Assuming the API endpoint for question generation is 'http://api.example.com/generateQuestions'
    const apiUrl = 'http://localhost:5000/mcq';
    const apiResponse = await axios.post(apiUrl, { text: data.text });
    console.log(apiResponse.data);
    
    return res.status(200).json(apiResponse.data);
  } catch (error) {
    console.error('Error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});