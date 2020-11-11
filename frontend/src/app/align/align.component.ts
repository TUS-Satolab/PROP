import { Component, OnInit, ViewChild } from '@angular/core';
import { formatDate } from '@angular/common';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { MessageService } from '../message.service';
import { ALIGN_URL, VERSION } from '../globals';
import { CookieService } from 'ngx-cookie-service';
import * as arrList from '../env.json'

@Component({
  selector: 'app-align',
  templateUrl: './align.component.html',
  styleUrls: ['./align.component.css'],
})
export class AlignComponent implements OnInit {
  @ViewChild('fileInput', { static: false }) fileInput: any;
  form: FormGroup;
  filename = '';
  _originalData = [];
  size_flag = 0;
  submit_flag = 0;

  constructor(
    private cookieService: CookieService,
    public fb: FormBuilder,
    private httpClient: HttpClient,
    private messageService: MessageService
  ) {}

  ngOnInit() {
    this.form = this.fb.group({
      file: ['', Validators.required],
      align_clw_opt: [''],
      align_method: ['mafft', Validators.required],
      input_type: [{ value: 'nuc', disabled: false }, Validators.required],
    });
    this._originalData = this.form.value;
    this.messageService.setDocuFlag('off');
  }
  // reset() {
  //   this.form.reset();
  // }

  reset() {
    this.form.setValue(this._originalData);
    this.filename = '';
    this.size_flag = 0;
  }

  onFileSelect(event) {
    if (event.target.files.length === 1) {
      // const file = event.target.files[0];
      // this.form.get('file').setValue(file);
      // this.filename = file.name;
      // this.fileInput.nativeElement.value = null;
      this.filename = '';
      this.form.get('file').setValue('');
      const file = event.target.files[0];
      // var upload = document.getElementById('browse');
      var upload = this.fileInput.nativeElement;
      if (upload.files[0].size > 20000000) {
        this.size_flag = 1;
        this.fileInput.nativeElement.value = null;
      } else {
        this.size_flag = 0;
        this.form.get('file').setValue(file);
        this.filename = file.name;
        this.fileInput.nativeElement.value = null;
      }
    }
  }

  onSubmit() {
    const formData: any = new FormData();
    let res: [''];
    const dateTime = formatDate(new Date(), 'yyyy/MM/dd HH:mm', 'en');
    const headers: HttpHeaders | {} = String(arrList.env[1].local_flag) === '1' ? new HttpHeaders({'Apikey': String(arrList.env[2].apikey),}) : {}

    const httpOptions: { headers; observe } = {
      headers: new HttpHeaders({
        'Content-Type': 'text/plain',
      }),
      observe: 'response',
    };

    formData.append('align_clw_opt', this.form.get('align_clw_opt').value);
    formData.append('file', this.form.get('file').value);
    formData.append('input_type', this.form.get('input_type').value);
    formData.append('align_method', this.form.get('align_method').value);
    // return this.httpClient.post(ALIGN_URL, formData).subscribe(data => {
    //   console.log(data);
    // });
    this.submit_flag = 1;
    return this.httpClient
      .post(ALIGN_URL, formData, {
        headers, observe: 'response',
      })
      .subscribe((data) => {
        var unparsed_id = data.body['task_id'];
        var parsed_id = unparsed_id.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        var unparsed_msg = data.body['msg'];
        var parsed_msg = unparsed_msg.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        this.messageService.add_msg({
          id: parsed_id,
          msg: parsed_msg,
          time: dateTime,
        });
        const allCookies: {} = this.cookieService.getAll();
        let i = Object.keys(allCookies).length + 1;
        // console.log(i);
        if (parsed_id !== 'None') {
          // this.cookieService.set(String ( i ), parsed_id);
          this.cookieService.set(
            String(i),
            parsed_id + ';' + parsed_msg + ';' + dateTime + ';' + i + ';' + 'align' + ';' + VERSION
          );
          this.submit_flag = 0;
        }
      });
    // this.httpClient.post(ALIGN_URL, formData).subscribe(
    //   (res) => console.log(res),
    //   (err) => console.log(err)
    // );
  }

  noalign() {
    if (this.form.get('align_method').value === 'None') {
      // this.form.controls['align_clw_opt'].reset();
      this.form.get('align_clw_opt').setValue('');
      return true;
    }
  }
}
