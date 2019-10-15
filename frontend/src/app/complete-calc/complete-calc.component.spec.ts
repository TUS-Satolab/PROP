import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CompleteCalcComponent } from './complete-calc.component';

describe('CompleteCalcComponent', () => {
  let component: CompleteCalcComponent;
  let fixture: ComponentFixture<CompleteCalcComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CompleteCalcComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CompleteCalcComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
