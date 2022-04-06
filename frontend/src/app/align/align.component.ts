import { Component, OnInit, ViewChild } from '@angular/core';
import { formatDate } from '@angular/common';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
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

  reset() {
    this.form.setValue(this._originalData);
    this.filename = '';
    this.size_flag = 0;
  }

  onFileSelect(event) {
    if (event.target.files.length === 1) {
      this.filename = '';
      this.form.get('file').setValue('');
      const file = event.target.files[0];
      var upload = this.fileInput.nativeElement;
      if (upload.files[0].size > Number(arrList['FILE_SIZE_LIMIT'])) {
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
    const headers: HttpHeaders | {} = String(arrList['LOCAL_FLAG']) === '1' ? new HttpHeaders({'Apikey': String(arrList['APIKEY']),}) : {}

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
        let count = 0 
        for (const key in allCookies) {
          if (key.startsWith("CANALPROJECT")) {
            let keySplit = key.split('.');
            count = Number(keySplit[1]) > count ? Number(keySplit[1]) : count;
          }
        }
        count++

        if (parsed_id !== 'None') {
          this.cookieService.set(
            "CANALPROJECT."+String(count),
            parsed_id + ';' + parsed_msg + ';' + dateTime + ';' + count + ';' + 'align' + ';' + String(VERSION), 
            7,'','',true,"None"
          );
          this.submit_flag = 0;
        }
      });
  }

  noalign() {
    if (this.form.get('align_method').value === 'None') {
      this.form.get('align_clw_opt').setValue('');
      return true;
    }
  }
}
