var express = require('express');
var router = express.Router();
const db = require('../db.js');
let converter = require('xml-js');
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
        var options = {ignoreComment: true, alwaysChildren: false, compact: true};
        arso_data_js = converter.xml2js(arso_data_xml, options);
        arso_data = arso_data_js['arsopodatki']['postaja'];
        resolve(arso_data);
      });
  
    }).on("error", (err) => {
      console.log("Error: " + err.message);
    });
    req.end();
  });
}

function insert_arso_data_MB(arso_data, id){
  var mb_titova = arso_data[4];
  if(mb_titova['merilno_mesto']['_text'] == 'MB Titova'){
    mb_titova_dict = arso_data_to_dict(mb_titova);
    db.insertArsoMeasurement(mb_titova_dict, id);
  }
  var mb_vrbanski = arso_data[5];
  if(mb_vrbanski['merilno_mesto']['_text'] == 'MB Vrbanski'){
    mb_vrbanski_dict = arso_data_to_dict(mb_vrbanski);
    db.insertArsoMeasurement(mb_vrbanski_dict, id);
  }
}

function arso_data_to_dict(arso_data){
  const arso_dict = {
    merilno_mesto : arso_data?.['merilno_mesto']?.['_text'],
    datum_od : arso_data?.['datum_od']?.['_text'],
    datum_do : arso_data?.['datum_do']?.['_text'],
    so2 : arso_data?.['so2']?.['_text'],
    co : arso_data?.['co']?.['_text'],
    o3 : arso_data?.['o3']?.['_text'],
    no2 : arso_data?.['no2']?.['_text'],
    pm10 : arso_data?.['pm10']?.['_text'],
    pm25 : arso_data?.['pm2.5']?.['_text'],
    benzen : arso_data?.['benzen']?.['_text'],
  }
  return arso_dict;
}



module.exports = router;
