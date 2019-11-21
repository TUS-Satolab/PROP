import { Component, OnInit } from '@angular/core';
import {formatDate} from '@angular/common';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { MessageService } from '../message.service';
import { ALIGN_URL } from '../globals';
import { CookieService } from 'ngx-cookie-service';

@Component({
  selector: 'app-align',
  templateUrl: './align.component.html',
  styleUrls: ['./align.component.css']
})
export class AlignComponent implements OnInit {
  // ALIGN_URL = 'http://52.198.155.126:5004/alignment';
  form: FormGroup;

  constructor(private cookieService: CookieService, public fb: FormBuilder, private httpClient: HttpClient,
              private messageService: MessageService) { }

  ngOnInit() {
    this.form = this.fb.group({
      file: ['', Validators.required],
      align_clw_opt: [''],
      align_method: ['clustalw', Validators.required],
      input_type: [{value: 'nuc', disabled: false}, Validators.required],
    });
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
    let res: [''];
    const dateTime = formatDate(new Date(), 'yyyy/MM/dd HH:mm', 'en');

    const httpOptions: { headers; observe; } = {
      headers: new HttpHeaders({
        'Content-Type':  'text/plain'
      }),
      observe: 'response'
    };

    formData.append('align_clw_opt', this.form.get('align_clw_opt').value);
    formData.append('file', this.form.get('file').value);
    formData.append('input_type', this.form.get('input_type').value);
    formData.append('align_method', this.form.get('align_method').value);
    // return this.httpClient.post(ALIGN_URL, formData).subscribe(data => {
    //   console.log(data);
    // });
    return this.httpClient.post(ALIGN_URL, formData, {
      observe: 'response'
    }).subscribe(data => {
      var unparsed_id = data.body["task_id"];
      var parsed_id = unparsed_id.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
      var unparsed_msg = data.body["msg"];
      var parsed_msg = unparsed_msg.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
      this.messageService.add_msg({id: parsed_id, msg: parsed_msg, time: dateTime});
      const allCookies: {} = this.cookieService.getAll();
      let i = Object.keys(allCookies).length + 1;
      // console.log(i);
      if (parsed_id !== 'None') {
        // this.cookieService.set(String ( i ), parsed_id);
        this.cookieService.set(String ( i ), parsed_id + ';' + parsed_msg + ';' + dateTime + ';' + i + ';' + 'align');
      }
    });
    // this.httpClient.post(ALIGN_URL, formData).subscribe(
    //   (res) => console.log(res),
    //   (err) => console.log(err)
    // );
  }


}
