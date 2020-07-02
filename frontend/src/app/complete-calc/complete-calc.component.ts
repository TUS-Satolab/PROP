import { Component, OnInit, ViewChild } from '@angular/core';
import { formatDate } from '@angular/common';
import { FormBuilder, FormGroup, FormControl, Validators } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { MessageService } from '../message.service';
import { SERVER_URL, VERSION } from '../globals';
import { CookieService } from 'ngx-cookie-service';
import { checkstatus } from '../checkstatus.service';
import { image } from 'd3';

@Component({
  selector: 'app-complete-calc',
  templateUrl: './complete-calc.component.html',
  styleUrls: ['./complete-calc.component.css'],
})
export class CompleteCalcComponent implements OnInit {
  @ViewChild('fileInput', { static: false }) fileInput: any;
  form: FormGroup;
  filename = '';
  _originalData = [];
  plusgapflag = 0;
  size_flag = 0;
  submit_flag = 0;

  constructor(
    private _checkstatus: checkstatus,
    private cookieService: CookieService,
    public fb: FormBuilder,
    private httpClient: HttpClient,
    private messageService: MessageService
  ) {}
  differences = ['P', 'K2P'];
  ngOnInit() {
    this.form = this.fb.group({
      file: ['', Validators.required],
      align_method: ['clustalw', Validators.required],
      input_type: [{ value: 'nuc', disabled: false }, Validators.required],
      gapdel: ['plusgap'],
      model: ['K2P', Validators.required],
      plusgap: [''],
      tree: ['nj', Validators.required],
      align_clw_opt: [''],
    });
    this._originalData = this.form.value;
    this.messageService.setDocuFlag('off');
  }
  onTypeSelect(input) {
    // var differences = [''];
    if (input == 'nuc') {
      this.form.get('model').setValue('K2P');
      this.differences = ['P', 'K2P'];
    } else if (input == 'ami') {
      this.form.get('model').setValue('Poisson');
      this.differences = ['P', 'Poisson'];
    }
    return this.differences;
  }

  reset() {
    this.form.setValue(this._originalData);
    this.filename = '';
    this.differences = ['P', 'K2P'];
    this.size_flag = 0;
  }

  onFileSelect(event) {
    if (event.target.files.length === 1) {
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
      // this.form.get('file').setValue(file);
      // this.filename = file.name;
    }
  }

  onSubmit() {
    const formData: any = new FormData();
    const dateTime = formatDate(new Date(), 'yyyy/MM/dd HH:mm', 'en');
    formData.append('file', this.form.get('file').value);
    formData.append('align_method', this.form.get('align_method').value);
    formData.append('input_type', this.form.get('input_type').value);
    if (this.form.get('model').value === 'Poisson') {
      formData.append('model', 'PC');
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
    formData.append('tree', this.form.get('tree').value);
    formData.append('align_clw_opt', this.form.get('align_clw_opt').value);
    this.submit_flag = 1;
    return this.httpClient
      .post(SERVER_URL, formData, {
        observe: 'response',
      })
      .subscribe((data) => {
        var unparsed_id = data.body['task_id'];
        var parsed_id: string = unparsed_id.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        var unparsed_msg = data.body['msg'];
        var parsed_msg: string = unparsed_msg.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        this.messageService.add_msg({
          id: parsed_id,
          msg: parsed_msg,
          time: dateTime,
        });
        const allCookies: {} = this.cookieService.getAll();
        let i = Object.keys(allCookies).length + 1;
        console.log(parsed_id);
        this.cookieService.set(
          String(i),
          parsed_id + ';' + parsed_msg + ';' + dateTime + ';' + i + ';' + 'complete' + ';' + String(VERSION)
        );
        this.submit_flag = 0;
      });
  }

  plusgapselected() {
    if (this.form.get('plusgap').value === true) {
      this.plusgapflag = 0;
      this.form.controls['gapdel'].reset();
      // this.form.controls['gapdel'].disable();
      return true;
    } else {
      this.plusgapflag = 1;
      // value could not be set here so it is set on submit
      // this.form.controls['gapdel'].setValue('pair');
    }
  }
  noalign() {
    if (this.form.get('align_method').value === 'None') {
      // this.form.controls['align_clw_opt'].reset();
      this.form.get('align_clw_opt').setValue('');
      return true;
    }
  }
}
