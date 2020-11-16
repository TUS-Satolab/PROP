import { Component, OnInit, ViewChild } from '@angular/core';
import { formatDate } from '@angular/common';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { MessageService } from '../message.service';
import { TREE_URL, VERSION } from '../globals';
import { CookieService } from 'ngx-cookie-service';
import * as arrList from '../env.json'

@Component({
  selector: 'app-tree',
  templateUrl: './tree.component.html',
  styleUrls: ['./tree.component.css'],
})
export class TreeComponent implements OnInit {
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
      tree: ['nj', Validators.required],
      file: ['', Validators.required],
      task_id: [''],
    });
    this._originalData = this.form.value;
    this.messageService.setDocuFlag('off');
  }

  onFileSelect(event) {
    if (event.target.files.length === 1) {
      this.filename = '';
      this.form.get('file').setValue('');
      const file = event.target.files[0];
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

  reset() {
    this.form.setValue(this._originalData);
    this.filename = '';
    this.size_flag = 0;
  }

  onSubmit() {
    const headers: HttpHeaders | {} = String(arrList.env[1].local_flag) === '1' ? new HttpHeaders({'Apikey': String(arrList.env[2].apikey),}) : {}
    const formData: any = new FormData();
    const dateTime = formatDate(new Date(), 'yyyy/MM/dd HH:mm', 'en');
    formData.append('tree', this.form.get('tree').value);
    formData.append('file', this.form.get('file').value);
    formData.append('task_id', this.form.get('task_id').value);
    this.submit_flag = 1;
    if (this.form.get('file').value === '' && this.form.get('task_id').value === '') {
      return this.messageService.add_msg('Add either a file or a task ID');
    } else {
      return this.httpClient.post(TREE_URL, formData, { headers, observe: 'response' }).subscribe((data) => {
        var unparsed_id = data.body['task_id'];
        var parsed_id = unparsed_id.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        var unparsed_msg = data.body['msg'];
        var parsed_msg = unparsed_msg.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        this.messageService.add_msg({ id: parsed_id, msg: parsed_msg, time: dateTime });
        
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
            parsed_id + ';' + parsed_msg + ';' + dateTime + ';' + count + ';' + 'tree' + ';' + String(VERSION), 7
          );
          this.submit_flag = 0;
        }
      });
    }
  }
}
