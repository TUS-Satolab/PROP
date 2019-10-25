import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { ReactiveFormsModule} from '@angular/forms';
import { HttpClientModule} from '@angular/common/http';
import { PopoverModule } from 'ngx-smart-popover';
import { CookieService } from 'ngx-cookie-service';



import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { AlignComponent } from './align/align.component';
import { MessagesComponent } from './messages/messages.component';
import { GetResultComponent } from './get-result/get-result.component';
import { CompleteCalcComponent } from './complete-calc/complete-calc.component';
import { MatrixComponent } from './matrix/matrix.component';
import { TreeComponent } from './tree/tree.component';
import { FooterComponent } from './footer/footer.component';
import { HeaderComponent } from './header/header.component';

@NgModule({
  declarations: [
    AppComponent,
    AlignComponent,
    MessagesComponent,
    GetResultComponent,
    CompleteCalcComponent,
    MatrixComponent,
    TreeComponent,
    FooterComponent,
    HeaderComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    ReactiveFormsModule,
    HttpClientModule,
    PopoverModule
  ],
  providers: [ CookieService ],
  bootstrap: [ AppComponent ]
})
export class AppModule { }
