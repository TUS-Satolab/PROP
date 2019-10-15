import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AlignComponent } from './align/align.component';
import { CompleteCalcComponent } from './complete-calc/complete-calc.component';
import { MessagesComponent } from './messages/messages.component';



const routes: Routes = [
  { path: '', redirectTo: 'align', pathMatch: 'full' },
  { path: 'align', component: AlignComponent },
  { path: 'complete', component: CompleteCalcComponent },
  { path: 'messages', component: MessagesComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
