import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DictionaryListComponent } from './dictionary-list.component';

describe('DictionaryListComponent', () => {
  let component: DictionaryListComponent;
  let fixture: ComponentFixture<DictionaryListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DictionaryListComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DictionaryListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
