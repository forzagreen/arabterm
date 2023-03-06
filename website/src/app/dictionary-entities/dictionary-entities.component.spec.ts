import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DictionaryEntitiesComponent } from './dictionary-entities.component';

describe('DictionaryEntitiesComponent', () => {
  let component: DictionaryEntitiesComponent;
  let fixture: ComponentFixture<DictionaryEntitiesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DictionaryEntitiesComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DictionaryEntitiesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
