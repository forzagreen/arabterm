import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { RouterModule } from '@angular/router';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { DictionaryEntitiesComponent } from './dictionary-entities/dictionary-entities.component';
import { DictionaryListComponent } from './dictionary-list/dictionary-list.component';

@NgModule({
  declarations: [
    AppComponent,
    DictionaryEntitiesComponent,
    DictionaryListComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    RouterModule.forRoot([
      { path: '', component: DictionaryListComponent },
      { path: ':dictName', component: DictionaryEntitiesComponent },
    ]),
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
