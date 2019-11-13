import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormControl, Validators } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { MessageService } from '../message.service';
import { SERVER_URL } from '../globals';
import { CookieService } from 'ngx-cookie-service';

@Component({
  selector: 'app-complete-calc',
  templateUrl: './complete-calc.component.html',
  styleUrls: ['./complete-calc.component.css']
})
export class CompleteCalcComponent implements OnInit {
  // arrList = require('../env.json');
  // const first = 'http://';
  // const last = ':5004/complete';
  // const IP = String ( this.arrList.env[0].ip_address ) ;
  // IP = process.env.IP_ADDRESS;
  // SERVER_URL = String ( this.first + this.IP + this.last );
  // SERVER_URL = 'http://localhost:5004/complete';
  form: FormGroup;
  constructor(private cookieService: CookieService, public fb: FormBuilder,
              private httpClient: HttpClient, private messageService: MessageService) { }
  differences = ['P', 'JS', 'K2P']
  ngOnInit() {
    this.form = this.fb.group({
      file: ['', Validators.required],
      align_method: ['clustalw', Validators.required],
      input_type: [{value: 'nuc', disabled: false}, Validators.required],
      gapdel: [''],
      model: ['K2P', Validators.required],
      plusgap: [true],
      tree: ['nj', Validators.required],
      align_clw_opt: [''],
    });
  }

  onTypeSelect(input){
    // var differences = [''];
    if (input == 'nuc') {
      this.differences = ['P', 'JS', 'K2P'];
    } else if (input == 'ami') {
      this.differences = ['P', 'JS', 'PC'];
    };
    return this.differences
  }

  reset() {
    this.form.reset();
  }

  onFileSelect(event) {
    if (event.target.files.length === 1) {
      const file = event.target.files[0];
      this.form.get('file').setValue(file);
    }
  }
  onSubmit() {
    const formData: any = new FormData();
    formData.append('file', this.form.get('file').value);
    formData.append('align_method', this.form.get('align_method').value);
    formData.append('input_type', this.form.get('input_type').value);
    formData.append('gapdel', this.form.get('gapdel').value);
    formData.append('model', this.form.get('model').value);
    // console.log(this.form.get('plusgap').value);
    if (this.form.get('plusgap').value === true) {
      formData.append('plusgap', this.form.get('plusgap').value);
    }
    formData.append('tree', this.form.get('tree').value);
    formData.append('align_clw_opt', this.form.get('align_clw_opt').value);
    return this.httpClient.post(SERVER_URL, formData, {
      observe: 'response'
    }).subscribe(data => {
      // console.log(data);
      var unparsed_id = data.body["task_id"];
      var parsed_id = unparsed_id.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
      var unparsed_msg = data.body["msg"];
      var parsed_msg = unparsed_msg.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
      this.messageService.add_msg(parsed_msg);
      this.messageService.add_id(parsed_id);
      const allCookies: {} = this.cookieService.getAll();
      // console.log(Object.keys(allCookies).length);
      let i = Object.keys(allCookies).length + 1;
      // console.log(i);
      if (parsed_id !== 'None') {
        this.cookieService.set(String ( i ), parsed_id);
      }
    });
  };

  plusgapselected() {
    if (this.form.get('plusgap').value === true) {
      this.form.controls['gapdel'].reset();
      return true;
    }
  }
}
