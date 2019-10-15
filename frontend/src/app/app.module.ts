import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { ReactiveFormsModule} from '@angular/forms';
import { HttpClientModule} from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { AlignComponent } from './align/align.component';
import { MessagesComponent } from './messages/messages.component';
import { GetResultComponent } from './get-result/get-result.component';
import { CompleteCalcComponent } from './complete-calc/complete-calc.component';
import { MatrixComponent } from './matrix/matrix.component';

@NgModule({
  declarations: [
    AppComponent,
    AlignComponent,
    MessagesComponent,
    GetResultComponent,
    CompleteCalcComponent,
    MatrixComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    ReactiveFormsModule,
    HttpClientModule,
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
