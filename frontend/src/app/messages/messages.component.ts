import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { MessageService } from '../message.service';
import {PopoverModule} from 'ngx-smart-popover';
import { CookieService } from 'ngx-cookie-service';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { GET_RESULT_URL, QUERY_URL } from '../globals';
import { saveAs } from 'file-saver';
import { checkstatus } from '../checkstatus.service';
import * as d3 from 'd3';
import { phylotree } from 'phylotree';
import 'phylotree/build/phylotree.css';
import * as svg_download from 'save-svg-as-png';
import { Router } from '@angular/router';

@Component({
  selector: 'app-messages',
  templateUrl: './messages.component.html',
  styleUrls: ['./messages.component.css']
})
export class MessagesComponent implements OnInit {
  private cookieValue: string;
  prevIdArray = [];
  showButton = false;

  // Phylotree parameters
  form: FormGroup;
  phylotreeData: JSON;
  tree: any;
  out_tree: any;

  // tslint:disable-next-line: max-line-length
  constructor(private _checkstatus: checkstatus, private httpClient: HttpClient, private cookieService: CookieService, public messageService: MessageService, private router: Router) { }

  ngOnInit() {
    this.prevIdArray = this._checkstatus.getStatus();
    setInterval(() => {
      this._checkstatus.checkStatus();
      this.prevIdArray = this._checkstatus.getStatus();
   }, 5000);
  }

  downloadFiles(input) {
    const formData: any = new FormData();
    formData.set('result_id', input);
    formData.set('result_kind', 'complete');
    console.log(formData.get('result_id'))
    console.log(formData.get('result_kind'))
    console.log(input)
    this.httpClient.post(QUERY_URL, formData, {observe: 'response'}).subscribe(query => {
      if (query.body['msg'] === 'Finished') {
        this.httpClient.post(GET_RESULT_URL, formData, {responseType: 'arraybuffer'}).subscribe(data => {
          const blob = new Blob([data], {
            type: 'application/zip'
          });
          saveAs(blob, 'results.zip');
        });
      } else {

        // pass

        // var parsed = query.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        // this.messageService.add_msg(parsed);
      }
    });
  }

  deleteAllCookies() {
    this.cookieService.deleteAll();
  }

// Phylotree part
downloadTree() {
  // console.log(this.out_tree.svg._groups[0][0])
  svg_download.saveSvgAsPng(this.out_tree.svg._groups[0][0], "phylotree.png");
  // svg.svgAsPngUri(document.getElementById('tree_display'), {}, (uri) => {
  //   console.log('png base 64 encoded', uri);
  // });
}
showTree(input) {
  const formData: any = new FormData();
  const httpOptions: { headers: any; responseType: any; } = {
    headers: new HttpHeaders({
      responseType: 'application/json'
    }),
    responseType: 'application/json'
  };
  formData.append('result_id', input);
  formData.append('result_kind', 'tree');
  console.log(input)
  this.httpClient.post(QUERY_URL, formData, {observe: 'response'}).subscribe(query => {
      if (query.body['msg'] === 'Finished') {
        this.httpClient.post(GET_RESULT_URL, formData, {responseType: 'text'}).subscribe(data => {
          this.tree = new phylotree(data);
          let svg = document.createElement('div');
          svg.setAttribute('id', 'tree_display');
          document.body.appendChild(svg);
          this.out_tree = this.tree.render(
            '#tree_display',
            {
              height: 500,
              width: 500,
              'left-right-spacing': 'fixed-step',
              'top-bottom-spacing': 'fixed-step',
              'minimum-per-node-spacing': 15,
              'maximum-per-node-spacing': 100,
              'is-radial': false,
              'max-radius': 768,
            }
          );
          return this.out_tree
        });
      } else {

        // pass

        // var parsed = query.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        // this.messageService.add_msg(parsed);
      }
      this.showButton = true;
  });

    }
deleteTree() {
  d3.select('#tree_display').remove();
  this.showButton = false;
}

vertical_increase() {
  if (this.tree.display.phylotree.display.fixed_width[0] < this.tree.display.phylotree.display.options["maximum-per-node-spacing"]) {
    this.tree.display.phylotree.display.fixed_width[0] = this.tree.display.phylotree.display.fixed_width[0] + 1;
    this.tree.display.update()
  }
}
vertical_decrease() {
  if (this.tree.display.phylotree.display.fixed_width[0] > this.tree.display.phylotree.display.options["minimum-per-node-spacing"]) {
    this.tree.display.phylotree.display.fixed_width[0] = this.tree.display.phylotree.display.fixed_width[0] - 1;
    this.tree.display.update()
  }
}
horizontal_increase() {
  if (this.tree.display.phylotree.display.fixed_width[1] < this.tree.display.phylotree.display.options["maximum-per-node-spacing"]) {
    this.tree.display.phylotree.display.fixed_width[1] = this.tree.display.phylotree.display.fixed_width[1] + 1;
    this.tree.display.update()
  }
}
horizontal_decrease() {
  if (this.tree.display.phylotree.display.fixed_width[1] > this.tree.display.phylotree.display.options["minimum-per-node-spacing"]) {
    this.tree.display.phylotree.display.fixed_width[1] = this.tree.display.phylotree.display.fixed_width[1] - 1;
    this.tree.display.update()
  }
}
radial() {
  this.tree.display.phylotree.display.options["is-radial"] = true;
  this.tree.display.phylotree.display.options["minimum-per-node-spacing"] = 2;
  this.tree.display.update();
};
linear() {
  this.tree.display.phylotree.display.options["is-radial"] = false;
  this.tree.display.phylotree.display.options["minimum-per-node-spacing"] = 15;
  this.tree.display.update();
};

}
