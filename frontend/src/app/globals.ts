'use strict';

var SERVER_URL_TEMP = '';
var QUERY_URL_TEMP = '';
var GET_RESULT_URL_TEMP = '';
var ALIGN_URL_TEMP = '';
var MATRIX_URL_TEMP = '';
var TREE_URL_TEMP = '';
var CANCEL_URL_TEMP = '';
export const VERSION = 6;

const arrList = require('./env.json');

if (String(arrList.env[1].local_flag) === '1') {
  var SERVER_URL_TEMP = 'http://localhost:5004/complete';
  var QUERY_URL_TEMP = 'http://localhost:5004/task_query';
  var GET_RESULT_URL_TEMP = 'http://localhost:5004/get_result_completed';
  var ALIGN_URL_TEMP = 'http://localhost:5004/alignment';
  var MATRIX_URL_TEMP = 'http://localhost:5004/matrix';
  var TREE_URL_TEMP = 'http://localhost:5004/tree';
  var CANCEL_URL_TEMP = 'http://localhost:5004/cancel_job';
} else {
  // var IP = String(arrList.env[0].ip_address);
  // var first = "https://";
  // var lastComplete = ":5004/complete";
  // var lastQuery = ":5004/task_query";
  // var lastResComp = ":5004/get_result_completed";
  // var lastAlign = ":5004/alignment";
  // var lastMatrix = ":5004/matrix";
  // var lastTree = ":5004/tree";
  // var lastCancel = ":5004/cancel_job";

  // var SERVER_URL_TEMP = String(first + IP + lastComplete);
  // var QUERY_URL_TEMP = String(first + IP + lastQuery);
  // var GET_RESULT_URL_TEMP = String(first + IP + lastResComp);
  // var ALIGN_URL_TEMP = String(first + IP + lastAlign);
  // var MATRIX_URL_TEMP = String(first + IP + lastMatrix);
  // var TREE_URL_TEMP = String(first + IP + lastTree);
  // var CANCEL_URL_TEMP = String(first + IP + lastCancel);
  var SERVER_URL_TEMP = 'https://9nrzjbva00.execute-api.ap-northeast-1.amazonaws.com/dev/complete';
  var QUERY_URL_TEMP = 'https://9nrzjbva00.execute-api.ap-northeast-1.amazonaws.com/dev/task_query';
  var GET_RESULT_URL_TEMP = 'https://9nrzjbva00.execute-api.ap-northeast-1.amazonaws.com/dev/get_result_completed';
  var ALIGN_URL_TEMP = 'https://9nrzjbva00.execute-api.ap-northeast-1.amazonaws.com/dev/alignment';
  var MATRIX_URL_TEMP = 'https://9nrzjbva00.execute-api.ap-northeast-1.amazonaws.com/dev/matrix';
  var TREE_URL_TEMP = 'https://9nrzjbva00.execute-api.ap-northeast-1.amazonaws.com/dev/tree';
  var CANCEL_URL_TEMP = 'https://9nrzjbva00.execute-api.ap-northeast-1.amazonaws.com/dev/cancel_job';
}

export const SERVER_URL = SERVER_URL_TEMP;
export const QUERY_URL = QUERY_URL_TEMP;
export const GET_RESULT_URL = GET_RESULT_URL_TEMP;
export const ALIGN_URL = ALIGN_URL_TEMP;
export const MATRIX_URL = MATRIX_URL_TEMP;
export const TREE_URL = TREE_URL_TEMP;
export const CANCEL_URL = CANCEL_URL_TEMP;
