import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { MessageService } from '../message.service';
import { Router } from '@angular/router';
import { saveAs } from 'file-saver';
import * as d3 from 'd3';
import { phylotree } from 'phylotree';
import 'phylotree/build/phylotree.css';
import { GET_RESULT_URL, QUERY_URL } from '../globals';


@Component({
  selector: 'app-get-result',
  templateUrl: './get-result.component.html',
  styleUrls: ['./get-result.component.css']
})
export class GetResultComponent implements OnInit {
  // GET_RESULT_URL = 'http://localhost:5004/get_result_completed';
  // QUERY_URL = 'http://localhost:5004/task_query';

  form: FormGroup;
  phylotreeData: JSON;


  constructor(public fb: FormBuilder, private httpClient: HttpClient,
              private messageService: MessageService, private router: Router) { }

  ngOnInit() {
    this.form = this.fb.group({
      result_id: [''],
      result_kind: [''],
    });
  }
//   downloadFile(data: Response) {
//     const blob = new Blob([data], {type: 'application/zip'});
//     saveAs(blob, 'results.zip');
//  }
showTree() {
  const formData: any = new FormData();
  const httpOptions: { headers: any; responseType: any; } = {
    headers: new HttpHeaders({
      responseType: 'application/json'
    }),
    responseType: 'application/json'
  };
  formData.append('result_id', this.form.get('result_id').value);
  formData.append('result_kind', 'tree');
  this.httpClient.post(QUERY_URL, formData, {responseType: 'text'}).subscribe(query => {
      if (query === 'Finished') {
        console.log(query);
        this.httpClient.post(GET_RESULT_URL, formData, {responseType: 'text'}).subscribe(data => {
          console.log(data)
          let tree = new phylotree(data);
          const height = 900;
          const width = 900;
          let svg = document.createElement('div');
          svg.setAttribute('id', 'tree_display');
          document.body.appendChild(svg);
          tree.render(
            '#tree_display', {
              height:height,
              width:width,
              'left-right-spacing': 'fit-to-size',
              'top-bottom-spacing': 'fit-to-size'
            }
  );
        });
      } else {
        console.log(query);
        var parsed = query.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        this.messageService.add(parsed);
      }
  });
  // var example_tree = "(((EELA:0.150276,CONGERA:0.213019):0.230956,(EELB:0.263487,CONGERB:0.202633):0.246917):0.094785,((CAVEFISH:0.451027,(GOLDFISH:0.340495,ZEBRAFISH:0.390163):0.220565):0.067778,((((((NSAM:0.008113,NARG:0.014065):0.052991,SPUN:0.061003,(SMIC:0.027806,SDIA:0.015298,SXAN:0.046873):0.046977):0.009822,(NAUR:0.081298,(SSPI:0.023876,STIE:0.013652):0.058179):0.091775):0.073346,(MVIO:0.012271,MBER:0.039798):0.178835):0.147992,((BFNKILLIFISH:0.317455,(ONIL:0.029217,XCAU:0.084388):0.201166):0.055908,THORNYHEAD:0.252481):0.061905):0.157214,LAMPFISH:0.717196,((SCABBARDA:0.189684,SCABBARDB:0.362015):0.282263,((VIPERFISH:0.318217,BLACKDRAGON:0.109912):0.123642,LOOSEJAW:0.397100):0.287152):0.140663):0.206729):0.222485,(COELACANTH:0.558103,((CLAWEDFROG:0.441842,SALAMANDER:0.299607):0.135307,((CHAMELEON:0.771665,((PIGEON:0.150909,CHICKEN:0.172733):0.082163,ZEBRAFINCH:0.099172):0.272338):0.014055,((BOVINE:0.167569,DOLPHIN:0.157450):0.104783,ELEPHANT:0.166557):0.367205):0.050892):0.114731):0.295021)"
  // // tree from Yokoyama et al http://www.ncbi.nlm.nih.gov/pubmed/18768804
  // let tree = new phylotree(example_tree);
  // const height = 900;
  // const width = 900;
  // let svg = document.createElement('div');
  // svg.setAttribute('id', 'tree_display');
  // document.body.appendChild(svg);
  // tree.render(
  //   '#tree_display', {
  //     height:height,
  //     width:width,
  //     'left-right-spacing': 'fit-to-size',
  //     'top-bottom-spacing': 'fit-to-size'
  //   }
  // );
    }
deleteTree() {
  d3.select('#tree_display').remove();
}

  onSubmit() {
    const formData: any = new FormData();
    let res: [''];

    const httpOptions: { headers: any; responseType: any; } = {
      headers: new HttpHeaders({
        responseType: 'application/zip'
      }),
      responseType: 'application/zip'
    };
    formData.append('result_id', this.form.get('result_id').value);
    formData.append('result_kind', 'complete');
    this.httpClient.post(QUERY_URL, formData, {responseType: 'text'}).subscribe(query => {
      if (query === 'Finished') {
        console.log(query);
        this.httpClient.post(GET_RESULT_URL, formData, {responseType: 'arraybuffer'}).subscribe(data => {
          const blob = new Blob([data], {
            type: 'application/zip'
          });
          saveAs(blob, 'results.zip');
        });
      } else {
        console.log(query);
        var parsed = query.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        this.messageService.add_msg(parsed);
      }
    });
  }
}
