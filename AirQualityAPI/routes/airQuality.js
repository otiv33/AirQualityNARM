var express = require('express');
var router = express.Router();
const db = require('../db.js');
let xmlParser = require('xml2json');
const https = require('https');

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
  try {
    const id = await db.insertLocalMeasurement(local_measurement);
    arso_data = await get_arso_data();
    insert_arso_data_MB(arso_data, id);
    res.json({ message: "Inserted measurement" });
  } catch (error) {
    console.log(error);
  }

});



async function get_arso_data(){
  return new Promise(async (resolve, reject) => {
    var req = https.get('https://www.arso.gov.si/xml/zrak/ones_zrak_urni_podatki_zadnji.xml', (resp) => {
      let arso_data_xml = '';
      resp.on('data', (chunk) => {
        arso_data_xml += chunk;
      });
      resp.on('end', () => {
        arso_data_json = xmlParser.toJson(arso_data_xml);
        arso_data = JSON.parse(arso_data_json)
        resolve(arso_data);
      });
  
    }).on("error", (err) => {
      console.log("Error: " + err.message);
    });
    req.end();
  });
}

function insert_arso_data_MB(arso_data, id){
  var mbTitova = arso_data['arsopodatki']['postaja'][4];
  if(mbTitova['merilno_mesto'] == 'MB Titova'){
    db.insertArsoMeasurement(mbTitova, id);
  }
  var mbVrbanski = arso_data['arsopodatki']['postaja'][5];
  if(mbVrbanski['merilno_mesto'] == 'MB Vrbanski'){
    db.insertArsoMeasurement(mbVrbanski, id);
  }
}


module.exports = router;
