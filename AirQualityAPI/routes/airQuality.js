var express = require('express');
var router = express.Router();
const db = require('../db.js');
let xmlParser = require('xml2json');

// GET air quality measurements
router.get('/', async function(req, res) {
  res.setHeader('Content-Type', 'application/json');
  const body = await db.getMeasurements();
  res.end(JSON.stringify(body));
});

// POST air quality measurements
router.post('/', async function(req, res) {
  local_measurement = req.body;
  console.log('Received post req : '+JSON.stringify(local_measurement));

  // GET ARSO measurements
  arso_data_xml = await get_arso_data();
  arso_data_json = xmlParser.toJson(arso_data_xml);
  arso_measurements = get_arso_data_MB(JSON.parse(arso_data_json));

  var arso_id = db.insertLocalMeasurement(arso_measurements);
  db.insertLocalMeasurement(local_measurement, arso_id);
  res.json({ message: "Inserted measurement" });
});


const https = require('https');
function get_arso_data(){
  return https.get('https://www.arso.gov.si/xml/zrak/ones_zrak_urni_podatki_zadnji.xml', (resp) => {
    let data = '';
    resp.on('data', (chunk) => {
      data += chunk;
    });
    resp.on('end', () => {
      return data;
    });

  }).on("error", (err) => {
    console.log("Error: " + err.message);
  });
}

function get_arso_data_MB(arso_data){
  
}


module.exports = router;
