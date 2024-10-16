import { Component, OnInit, ViewChild } from '@angular/core';
import { formatDate } from '@angular/common';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { MessageService } from '../message.service';
import { MATRIX_URL, VERSION } from '../globals';
import { environment } from '../../environments/environment';
import { CookieService } from 'ngx-cookie-service';

@Component({
  selector: 'app-matrix',
  templateUrl: './matrix.component.html',
  styleUrls: ['./matrix.component.css'],
})
export class MatrixComponent implements OnInit {
  @ViewChild('fileInput', { static: false }) fileInput: any;
  form: FormGroup;
  filename = '';
  _originalData = [];
  differences = ['P-distance', 'K2P'];
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
      input_type: [{ value: 'nuc', disabled: false }, Validators.required],
      gapdel: ['plusgap'],
      model: ['K2P', Validators.required],
      plusgap: [''],
      file: ['', Validators.required],
      task_id: [''],
    });
    this._originalData = this.form.value;
    this.messageService.setDocuFlag('off');
  }

  onTypeSelect(input) {
    if (input === 'nuc') {
      this.form.get('model').setValue('K2P');
      this.differences = ['P-distance', 'K2P'];
    } else if (input === 'ami') {
      this.form.get('model').setValue('JC');
      this.differences = ['P-distance', 'JC'];
    }
    return this.differences;
  }

  reset() {
    this.form.setValue(this._originalData);
    this.filename = '';
    this.differences = ['P-distance', 'K2P'];
    this.size_flag = 0;
  }

  onFileSelect(event) {
    if (event.target.files.length === 1) {
      this.filename = '';
      this.form.get('file').setValue('');
      const file = event.target.files[0];
      const upload = this.fileInput.nativeElement;
      if (upload.files[0].size > Number(environment.fileSizeLimit)) {
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
    const headers: HttpHeaders = new HttpHeaders({'Apikey': environment.apiKey});
    const formData: any = new FormData();
    const dateTime = formatDate(new Date(), 'yyyy/MM/dd HH:mm', 'en');
    formData.append('file', this.form.get('file').value);
    formData.append('task_id', this.form.get('task_id').value);
    formData.append('input_type', this.form.get('input_type').value);
    if (this.form.get('model').value === 'JC') {
      formData.append('model', 'JC');
    } else {
      formData.append('model', this.form.get('model').value);
    }
    if (this.form.get('gapdel').value === 'plusgap') {
      formData.append('plusgap', 'checked');
      formData.append('gapdel', 'null');
    } else {
      formData.append('plusgap', 'not_checked');
      formData.append('gapdel', this.form.get('gapdel').value);
    }

    this.submit_flag = 1;
    if (this.form.get('file').value === '' && this.form.get('task_id').value === '') {
      return this.messageService.add_msg('Add either a file or a task ID');
    }
      return this.httpClient.post(MATRIX_URL, formData, { headers, observe: 'response' }).subscribe((data) => {
        const unparsed_id = data.body['task_id'];
        const parsed_id = unparsed_id.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        const unparsed_msg = data.body['msg'];
        const parsed_msg = unparsed_msg.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        this.messageService.add_msg({ id: parsed_id, msg: parsed_msg, time: dateTime });
        const allCookies: {} = this.cookieService.getAll();
        let count = 0
        for (const key in allCookies) {
          if (key.startsWith("CANALPROJECT")) {
            const keySplit = key.split('.');
            count = Number(keySplit[1]) > count ? Number(keySplit[1]) : count;
          }
        }
        count++

        if (parsed_id !== 'None') {
          this.cookieService.set(
            `CANALPROJECT.${String(count)}`,
            `${parsed_id};${parsed_msg};${dateTime};${count};matrix;${String(VERSION)}`,
            7,'','',true,"None"
          );
          this.submit_flag = 0;
        }
      });
  }
  plusgapselected() {
    if (this.form.get('plusgap').value === true) {
      this.form.controls['gapdel'].reset();
      return true;
    }
      this.form.get('gapdel').setValue('pair');
  }
}
