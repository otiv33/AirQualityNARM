var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
const http = require('http');
const https = require('https');
const fs = require('fs');

// Rpoutes
var indexRouter = require('./routes/index');
var airQualityRouter = require('./routes/airQuality');

var app = express();

// Certificate
const privateKey = fs.readFileSync('/etc/letsencrypt/live/20.222.149.200/privkey.pem', 'utf8');
const certificate = fs.readFileSync('/etc/letsencrypt/live/20.222.149.200/cert.pem', 'utf8');
const ca = fs.readFileSync('/etc/letsencrypt/live/20.222.149.200/chain.pem', 'utf8');
const credentials = {
	key: privateKey,
	cert: certificate,
	ca: ca
};

// Read settings.json
const fs = require('fs');
let rawdata = fs.readFileSync('settings.json');
const settings = JSON.parse(rawdata);

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

// Basic authentication
app.use((req, res, next) => {
  const apiToken = req.headers.authorization;
  if(apiToken === settings.apiToken){
    return next();
  } else {
    res.status(401).send('Authentication required');
  } 
})

app.use('/', indexRouter);
app.use('/airQuality', airQualityRouter);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

const httpServer = http.createServer(app);
const httpsServer = https.createServer(credentials, app);

httpServer.listen(8080, () => {
  console.log(`Server is running on port 8080.`);
});

httpsServer.listen(443, () => {
  console.log(`Server is running on port 443.`);
});

module.exports = app;
