import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { Dictionary, dictionaries } from "../dictionaries";

export interface Entity {
  id: number;
  en: string;
  ar: string;
  fr: string;
  ge?: string;
  d?: string;
}

@Component({
  selector: 'app-dictionary-entities',
  standalone: false,
  templateUrl: './dictionary-entities.component.html',
  styleUrls: ['./dictionary-entities.component.css']
})
export class DictionaryEntitiesComponent {
  constructor(
    private route: ActivatedRoute,
    private http: HttpClient,
  ) { }

  dictionary?: Dictionary;
  entities!: Observable<Entity[]>;

  ngOnInit() {
    const routeParams = this.route.snapshot.paramMap;
    const dictNameFromRoute = routeParams.get('dictName');
    this.dictionary = dictionaries.find((dictionary) => dictionary.name === dictNameFromRoute)
    console.log(this.dictionary)
    this.entities = this.http.get<Entity[]>(`assets/${dictNameFromRoute}.json`);
  }
}
