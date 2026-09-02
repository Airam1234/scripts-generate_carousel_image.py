/**
 * Accessible Word version of In The Loop, September 2026 (learner edition).
 * Wording is kept identical to work/issue.html — the two files are emailed
 * together and read as one thing. build_docx.js turns this into real heading
 * styles, alt text and live links. The QR code in the PDF is replaced here by
 * the survey web address as a live link, since a screen reader cannot scan a QR.
 */
module.exports = {
  title: 'In The Loop',
  issue: 'CoreEd Learner Newsletter  |  Issue: September 2026',
  strapline: 'A monthly update for CoreEd learners.',
  description: 'Accessible version of the In The Loop learner newsletter, September 2026.',

  sections: [
    {
      heading: 'Welcome',
      blocks: [
        { type: 'p', text: 'Welcome to the September issue. The new academic year is under way, and there’s plenty in this one: results worth celebrating, a conversation that matters more than any other this month, National Inclusion Week, and keeping your momentum into autumn.' },
        { type: 'p', text: 'Whoever you are and wherever you’ve come from, you belong here at CoreEd.' },
        { type: 'p', text: 'As ever, Corrie, Ben, Priya and the Safety Guardian will point you to the useful bits.' },
        {
          type: 'image', file: 'characters/Mascot_Welcome.png', width: 90, height: 68,
          name: 'CoreEd Safety Guardian mascot',
          description: 'Illustration of the CoreEd Safety Guardian, a friendly shield-shaped mascot, waving hello.',
          caption: 'Illustration: the CoreEd Safety Guardian, waving hello.',
        },
        { type: 'h2', text: 'In this issue' },
        { type: 'bullets', items: [
          '01 — In Their Words',
          '02 — Your Voice, Your Say',
          '03 — Talking Saves Lives',
          '04 — Building Trust Together',
          '05 — Your Next Step',
          '06 — Safeguarding Team Update',
          '07 — Looking Out for One Another',
          '08 — Support & Resources',
        ]},
      ],
    },
    {
      heading: '01. In Their Words',
      blocks: [
        { type: 'p', text: 'A pharmacy apprentice’s feedback this month.' },
        { type: 'p', text: 'This month’s words come from a pharmacy apprentice who started on the 10-week bootcamp and is now working and studying in the sector:' },
        { type: 'callout', colour: 'blue', text: [
          '“I started with the 10-week pharmacy bootcamp, which gave me a great insight into what it would be like working in a pharmacy. My tutors, teachers and the staff at CoreEd have been especially supportive, and helped me at times when I found things a bit difficult. CoreEd helped me secure employment, which led me to start my apprenticeship. I feel very confident to be working in the pharmaceutical sector, and intend to continue developing my skills in pharmacy.”',
          '— A CoreEd pharmacy apprentice',
        ]},
        { type: 'p', text: 'Thank you for sharing. The wider picture backs it up: seven learners completed their apprenticeship in July, six passes and one distinction, taking this year’s total to 39 completions, almost half of them, 46%, distinctions. If you’d like your words to appear here, tell your tutor.' },
        {
          type: 'image', file: 'characters/Priya_Listening.png', width: 60, height: 108,
          name: 'Priya Shah, assessor',
          description: 'Illustration of Priya Shah, a CoreEd assessor, listening attentively.',
          caption: 'Illustration: Priya Shah, one of our assessors.',
        },
      ],
    },
    {
      heading: '02. Your Voice, Your Say',
      blocks: [
        { type: 'p', text: 'The survey that shapes CoreEd.' },
        { type: 'p', text: 'A new academic year is a good moment to tell us how things are going. We read every survey response, and what you tell us shapes what we do next: it is the most direct route from your experience to our decisions. It takes about two minutes, and it can be anonymous.' },
        { type: 'h2', text: 'Your say, in about two minutes' },
        { type: 'p', text: 'Not sure where to start? Tell us: one thing CoreEd does well, one thing we could do better, and one thing that would make your week easier.' },
        {
          type: 'link',
          before: 'Open the survey here: ',
          text: 'CoreEd learner survey',
          href: 'https://qualityhero.co.uk/f/40e945db4a76a23be6cf0b3dfe2147da7e59c95bb5b46ea9',
          after: '. The QR code in the printed version links to the same address, so you can scan it with your phone camera or ask your tutor to send it over.',
        },
        {
          type: 'link',
          before: 'We’re on Instagram too. Follow @coreedlimited at ',
          text: 'instagram.com/coreedlimited',
          href: 'https://www.instagram.com/coreedlimited',
          after: ' for day-to-day updates, celebrations and reminders between issues.',
        },
        {
          type: 'image', file: 'characters/Corrie_Proud.png', width: 60, height: 90,
          name: 'Corrie Patel, apprentice',
          description: 'Illustration of Corrie Patel, a CoreEd apprentice, standing proudly.',
          caption: 'Illustration: Corrie Patel, one of our apprentices.',
        },
      ],
    },
    {
      heading: '03. Talking Saves Lives',
      blocks: [
        { type: 'p', text: 'World Suicide Prevention Day, 10 September.' },
        { type: 'p', text: '10 September is World Suicide Prevention Day. This year’s theme is about changing the narrative on suicide: replacing silence and awkwardness with open, honest conversations. That starts with ordinary people, not experts.' },
        { type: 'h2', text: 'It’s okay to talk about it' },
        { type: 'p', text: 'If you’re struggling, you are not alone, and you don’t have to work it out by yourself. Talking about how you feel, including suicidal thoughts, does not make things worse. It is usually the first step to feeling less alone. And if you’re worried about a friend or a colleague, it’s okay to ask them directly how they’re doing. You don’t need the perfect words; listening without judgement matters far more.' },
        { type: 'h2', text: 'Support that’s there any time' },
        { type: 'callout', colour: 'blue', text: 'Samaritans: call 116 123, free, 24/7. Shout: text SHOUT to 85258. HOPELINE247 (for under-35s): call 0800 068 4141 or text 88247, any hour, any day. If someone is in immediate danger, call 999. And your tutor is always a safe place to start.' },
        { type: 'p', text: 'Youth Mental Health Day follows on 18 September with the theme #BuildFutureYou: a nudge that whatever the future holds, the next small step towards it is yours to take.' },
        {
          type: 'image', file: 'characters/Priya_Supportive.png', width: 60, height: 92,
          name: 'Priya Shah, assessor',
          description: 'Illustration of Priya Shah, a CoreEd assessor, offering supportive reassurance.',
          caption: 'Illustration: Priya Shah, one of our assessors.',
        },
      ],
    },
    {
      heading: '04. Building Trust Together',
      blocks: [
        { type: 'p', text: 'National Inclusion Week, 14 to 20 September.' },
        { type: 'p', text: 'National Inclusion Week runs from 14 to 20 September. This year’s theme is “Build Trust. Navigate Change.” Inclusion isn’t a policy on a shelf; it’s whether people feel safe to be themselves at work and in study.' },
        { type: 'h2', text: 'Small things build trust' },
        { type: 'p', text: 'Use people’s names and pronouns correctly. Bring the quiet person into the conversation. Ask rather than assume. Give credit where it’s due. None of this costs anything, and it adds up to a place where everyone can do their best work.' },
        { type: 'h2', text: 'Change is easier together' },
        { type: 'p', text: 'New term, new rotas, new faces. If a change at work or in your study is unsettling you, say so. Your tutor can help you plan around it, and reasonable adjustments are always worth a confidential conversation.' },
        {
          type: 'image', file: 'characters/Ben_Encouraging.png', width: 60, height: 97,
          name: 'Ben Carter, mentor',
          description: 'Illustration of Ben Carter, a CoreEd mentor, giving an encouraging thumbs up.',
          caption: 'Illustration: Ben Carter, one of our mentors.',
        },
      ],
    },
    {
      heading: '05. Your Next Step',
      blocks: [
        { type: 'p', text: 'Into the autumn with momentum.' },
        { type: 'p', text: 'The new academic year is a natural point to check where you are and what comes next. If English or maths Functional Skills are still on your list, check with your coach what applies to you and plan the next step together. Whatever stage you’re at, they’re here to help you move forward.' },
        { type: 'h2', text: 'Dates for your diary — September' },
        { type: 'bullets', items: [
          '8 September — International Literacy Day.',
          '10 September — World Suicide Prevention Day.',
          '14 to 20 September — National Inclusion Week.',
          '18 September — Youth Mental Health Day.',
          '23 September — International Day of Sign Languages.',
          '25 September — Macmillan Coffee Morning.',
        ]},
        {
          type: 'image', file: 'characters/Corrie_Thinking.png', width: 60, height: 90,
          name: 'Corrie Patel, apprentice',
          description: 'Illustration of Corrie Patel, a CoreEd apprentice, thinking about their next step.',
          caption: 'Illustration: Corrie Patel, one of our apprentices.',
        },
      ],
    },
    {
      heading: '06. Safeguarding Team Update',
      blocks: [
        { type: 'p', text: 'Know who to turn to this term.' },
        { type: 'p', text: 'Safeguarding is everyone’s responsibility. Whether it’s about your own wellbeing, someone else’s safety, or a difficult time, please reach out. Speaking up early is always the right thing to do, and raising a concern does not put your apprenticeship at risk.' },
        { type: 'contact', name: 'Jeannette Adrian', role: 'Designated Safeguarding Lead (DSL) and Wellbeing Support', phone: '07557 093701', email: 'jeannette@CoreEd.co.uk' },
        { type: 'contact', name: 'Airam Neesa', role: 'Deputy Designated Safeguarding Lead', phone: '07912 342 367', email: 'airam@CoreEd.co.uk' },
      ],
    },
    {
      heading: '07. Looking Out for One Another',
      blocks: [
        { type: 'p', text: 'New term, new group chats, same care.' },
        { type: 'p', text: 'September brings new cohorts, new chats and new feeds. Part of keeping everyone safe is something called Prevent. Here’s what it means, and who to talk to if something doesn’t feel right.' },
        { type: 'h2', text: 'Support, not suspicion' },
        { type: 'p', text: 'Prevent is part of safeguarding. It’s about helping anyone who might be at risk of being pulled towards extremism or hateful views, the same way we’d help with any other worry. It isn’t about getting anyone into trouble; it’s about getting the right support early.' },
        { type: 'h2', text: 'Question what you see' },
        { type: 'p', text: 'Not everything online is true or safe, and new group chats set their tone early. If a post, message or account makes you uneasy, or pressures you to do or believe something, step back and talk to someone you trust. Keep your details private and be kind in the chat.' },
        {
          type: 'link',
          before: 'Worried about something? You can speak to Jeannette or Airam (above), or contact the ACT Early support line on 0800 011 3764 or at ',
          text: 'actearly.uk',
          href: 'https://actearly.uk',
          after: '. In an emergency, always call 999.',
        },
        {
          type: 'image', file: 'characters/Mascot_Warning.png', width: 90, height: 66,
          name: 'CoreEd Safety Guardian mascot',
          description: 'Illustration of the CoreEd Safety Guardian with a hand raised in a gentle stop gesture.',
          caption: 'Illustration: the CoreEd Safety Guardian, with a hand raised.',
        },
      ],
    },
    {
      heading: 'Final thoughts',
      blocks: [
        { type: 'p', text: 'A new year, a fresh start. Look after yourselves and each other, keep talking, and do have your say in the survey. Congratulations to July’s completers!' },
        { type: 'p', text: '— The CoreEd Team', bold: true },
        {
          type: 'image', file: 'characters/Mascot_Celebration.png', width: 90, height: 61,
          name: 'CoreEd Safety Guardian mascot',
          description: 'Illustration of the CoreEd Safety Guardian celebrating with a thumbs up.',
          caption: 'Illustration: the CoreEd Safety Guardian, celebrating.',
        },
      ],
    },
    {
      heading: '08. Support & Resources',
      blocks: [
        { type: 'h2', text: 'Study & next steps' },
        { type: 'bullets', items: [
          'Your CoreEd tutor — your first port of call for options, Functional Skills and one-to-one help.',
          'National Careers Service — free careers advice and a helpline (nationalcareers.service.gov.uk).',
          'GOV.UK Apprenticeships — how apprenticeships and assessment work (gov.uk).',
        ]},
        { type: 'h2', text: 'Inclusion & belonging' },
        { type: 'bullets', items: [
          'Inclusive Employers — National Inclusion Week resources and ideas (inclusiveemployers.co.uk).',
          'National Literacy Trust — free reading and writing support for all ages (literacytrust.org.uk).',
          'Your CoreEd tutor — to arrange a reasonable adjustment or talk anything through.',
        ]},
        { type: 'h2', text: 'Wellbeing & mental health' },
        { type: 'bullets', items: [
          'Samaritans — free, 24/7; call 116 123 in the UK.',
          'Shout — free 24/7 text support; text SHOUT to 85258.',
          'HOPELINE247 (PAPYRUS) — for under-35s; call 0800 068 4141 or text 88247 (papyrus-uk.org).',
          'stem4 — youth mental health resources and apps (stem4.org.uk).',
          'Mind — mental health advice and local services (mind.org.uk).',
        ]},
      ],
    },
  ],
};
