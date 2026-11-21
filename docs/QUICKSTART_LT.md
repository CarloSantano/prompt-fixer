# Prompt Fixer: pradžia draugui

Rašyk savo mintis įprastai. Įrankis padės suformuluoti užduotį ir parodys, ką
pakeitė. Šiam paketui atskiro serverio ar API rakto nereikia; naudojamo AI
asistento prieiga ir jo naudojimo kaina lieka tavo aplinkos dalis.

## Codex arba Claude Code

1. Parsisiųsk repozitoriją per **Code → Download ZIP** ir išskleisk arba naudok
   `git clone https://github.com/CarloSantano/prompt-fixer.git`.
2. Pasirink savo projektą. Jei dar neturi, susikurk jam tuščią aplanką.
3. Nukopijuok **visą** `skills/prompt-fixer` aplanką su jo turiniu:

| Aplinka | Vieta tavo projekte |
| --- | --- |
| Codex | `.agents/skills/prompt-fixer/` |
| Claude Code | `.claude/skills/prompt-fixer/` |

Atverk arba perkrauk projektą asistente. Jo įgūdžių sąraše patikrink, ar matomas
`prompt-fixer`. Codex užklausa:

```text
$prompt-fixer noriu sukurti vidinį pardavimų įrankį sau, techninius dalykus pasirink pats
```

Claude Code pradėk nuo `/prompt-fixer` vietoje `$prompt-fixer`.

Turėtum pamatyti savo užklausą, pataisytą promptą ir trumpą paaiškinimą, kas
pakeista. Šiuo žingsniu pati programėlė dar nekuriama. Norėdamas tęsti, rašyk
**„vykdyk šį promptą“**. Jei nori vienu žingsniu, rašyk **„pagerink ir vykdyk
dabar“**. **„Tik galutinį promptą“** paslepia palyginimo blokus.

Jei turi Python 3.12+, gali naudoti diegimo pagalbininką iš
[README](../README.md#quick-install-codex-or-claude-code). Jis patikrina failus,
saugo atsargines kopijas ir atsisako perrašyti tavo pakeistus failus. Rankinis
kopijavimas diegimo kvito nesukuria.

## ChatGPT Work Mode

Jei tavo paskyroje galima kurti asmeninius įskiepius, iš
[Releases](https://github.com/CarloSantano/prompt-fixer/releases/latest) parsisiųsk
`prompt-fixer-v0.7.0.zip`. Pridėk jį Work Mode pokalbyje, kuriame prieinamas
Plugin Creator, ir parašyk:

```text
Sukurk man privatų asmeninį Prompt Fixer įskiepį iš pridėto archyvo.
```

Sukurtą įskiepį pasirink savo paskyroje ir žymėk jį užklausoje. Tai priklauso nuo
paskyros funkcijų; vien įklijuoti GitHub nuorodą į paprastą chatą neužtenka
automatiniam įdiegimui. Autoriaus privataus įskiepio prieiga neperkeliama.

## Pirmas patikrinimas

Paduok trumpą tikrą užduotį ir patikrink: originalas pacituotas teisingai, svarbūs
reikalavimai neprarasti, AI nepradėjo vykdyti projekto, kai prašei tik pataisymo.
Jei įgūdis neaptinkamas, patikrink aplanko vietą, `SKILL.md` bei visus
`references` ir perkrauk projekto sesiją. Automatinis pasirinkimas priklauso nuo
asistento, todėl pirmam bandymui naudok aiškų iškvietimą.
