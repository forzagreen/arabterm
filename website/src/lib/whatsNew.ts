// What returning visitors are told about in the «الجديد» panel of the header
// (components/WhatsNew.astro). Two kinds of news:
//
//  * Features: FEATURES below, written by hand. Only put there what a reader
//    of the site notices (a new link, a new column, a new page), in plain
//    Arabic, no code or version talk. Newest first; drop an entry once it is a
//    few months old, the list is meant to stay short. `media` names an
//    optional animation of the feature, drawn by WhatsNew.astro.
//
//  * Dictionaries: not listed here. The panel compares the dictionary ids
//    built into the page with the largest one the visitor has seen, so a new
//    dictionary announces itself with the next deploy, with no edit here.
//
// "Seen" lives in localStorage (same as the theme), so it is per browser:
// nothing is sent anywhere. A first visit records the current state
// silently (everything is new to a first-time visitor); from then on, unseen
// news opens the panel once, and closing it marks everything seen.
export interface Feature {
  // Keep the ids stable: they are what the browser remembers having seen.
  id: string;
  date: string; // YYYY-MM-DD, shown as month and year
  title: string;
  body: string;
  media?: 'page-link';
}

export const FEATURES: Feature[] = [
  {
    id: 'page-links',
    date: '2026-10-16',
    title: 'رقم الصفحة يفتح القاموس المصوّر',
    body:
      'في القواميس الورقية صار رقم الصفحة في جدول المصطلحات رابطًا: اضغط عليه لتفتح الصفحة نفسها من النسخة المصوّرة للقاموس على archive.org، فتتحقّق من المصطلح في مصدره مباشرة.',
    media: 'page-link',
  },
];

// "أكتوبر 2026": Arabic month name, Western digits like the rest of the site.
export function formatMonth(isoDate: string): string {
  const [year, month, day] = isoDate.split('-').map(Number);
  return new Intl.DateTimeFormat('ar-u-nu-latn', { month: 'long', year: 'numeric' }).format(
    new Date(year, month - 1, day)
  );
}
