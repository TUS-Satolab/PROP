import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { MessageService } from '../message.service';
import { saveAs } from 'file-saver';

@Component({
  selector: 'app-get-result',
  templateUrl: './get-result.component.html',
  styleUrls: ['./get-result.component.css']
})
export class GetResultComponent implements OnInit {
  SERVER_URL = 'http://localhost:5004/get_result_completed';
  form: FormGroup;

  constructor(public fb: FormBuilder, private httpClient: HttpClient, private messageService: MessageService) { }

  ngOnInit() {
    this.form = this.fb.group({
      result_id: [''],
    });
  }
//   downloadFile(data: Response) {
//     const blob = new Blob([data], {type: 'application/zip'});
//     saveAs(blob, 'results.zip');
//  }

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
    // return this.httpClient.post(this.SERVER_URL, formData, httpOptions).subscribe(data => {
    //   this.downloadFile(data);
    // });
    // return this.httpClient.post(this.SERVER_URL, formData, {responseType: 'arraybuffer'}
    // ).subscribe(data => {
    //   const blob = new Blob([data], {
    //     type: 'application/zip'
    //   });
    //   const url = window.URL.createObjectURL(blob);
    //   window.open(url);
    //   // this.downloadFile(data);
    // });
    this.httpClient.post('http://localhost:5004/task_query', formData, {responseType: 'text'}).subscribe(query => {
      if (query === 'Finished') {
        console.log(query);
        this.httpClient.post(this.SERVER_URL, formData, {responseType: 'arraybuffer'}).subscribe(data => {
          const blob = new Blob([data], {
            type: 'application/zip'
          });
          saveAs(blob, 'results.zip');
          // const url = window.URL.createObjectURL(blob);
          // window.open(url);
          // this.downloadFile(data);
        });
      } else {
        console.log(query);
        var parsed = query.replace(/(['"])?([a-z0-9A-Z_]+)(['"])?:/g, '"$2": ');
        this.messageService.add(parsed);
      }
    });
  }
}
