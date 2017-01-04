*** Setting ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  resource/common.robot
Resource  resource/keywords.robot

Test Setup        Prepare test browser
Test Teardown     Close all browsers

*** Test Case ***
General Language tests
    [Documentation]    testing of OiRA multiple European languages.
    Set Test Message    Translations need to be updated
    Given I am logged in as a user in OiRA EU
    Go To    ${PROTOCOL}://${SERVER}/cy/hairdressers/cyprus_hairdressers_el
    Click Button    next
    Wait Until Page Contains    Βοήθεια
    Wait Until Page Contains    Αξιολόγηση
    Wait Until Page Contains    Κύπρος: Κουρεία - Κομμωτήρια
    Wait Until Page Contains    Η εκτίμηση του κινδύνου δεν είναι περίπλοκη
    Go To    ${PROTOCOL}://${SERVER}/cy/civil-service/demosia-dioikese
    Click Button    next
    Wait Until Page Contains    Βοήθεια
    Wait Until Page Contains    Αξιολόγηση
    Wait Until Page Contains    Εργασίες Γραφείου - Δημόσια Διοίκηση
    Wait Until Page Contains    Μια αδιάφορη
    Wait Until Page Contains    Σχετικά
    Go To    ${PROTOCOL}://${SERVER}
    Go To    ${PROTOCOL}://${SERVER}/fr/transportroutier/transporoutier-2-parametres
    # Note: if the "Splash message" gets removed, the following line must go too
    # Wait until element is visible  css=hr.trigger.pat-switch
    # Click element  css=hr.trigger.pat-switch
    Click Button    next
    Wait Until Page Contains    Aide
    Wait Until Page Contains    Estimation
    Wait Until Page Contains    Transport routier
    Wait Until Page Contains    L'évaluation des risques professionnels (EvRP)
    Go To    ${PROTOCOL}://${SERVER}
    Go To    ${PROTOCOL}://${SERVER}/eu/leather-tanning/leather-tanning-draft-risk-assessment-tool
    # Note: if the "Splash message" gets removed, the following line must go too
    # Wait until element is visible  css=hr.trigger.pat-switch
    # Click element  css=hr.trigger.pat-switch
    Click Button    next
    Wait Until Page Contains    Help
    Wait Until Page Contains    Evaluation
    Wait Until Page Contains    Leather & Tanning
    Wait Until Page Contains    Goal of the risk assessment tool
    Go To    ${PROTOCOL}://${SERVER}

Language test fr button-name
    [Documentation]    (support #5932) testing of button-name "Accepter et continuer"
    Go To    ${PROTOCOL}://${SERVER}/fr/logout
    Go To    ${PROTOCOL}://${SERVER}/eu?set_language=en
    Click link "register"
    Register form should open
    Fill out and send register form
    Terms of conditions should open
    Wait Until Page Contains    Agree and continue
    Accept terms of conditions
    Go To    ${PROTOCOL}://${SERVER}/terms-and-conditions?set_language=fr
    Terms of conditions should open
    Wait Until Page Contains    Accepter et continuer
    Go To    ${PROTOCOL}://${SERVER}/eu/account-delete?set_language=en
    Confirm delete account action
    Account should be deleted

Test help headings en
    [Documentation]    (support #5648, #5170)
    Go To    ${PROTOCOL}://${SERVER}/eu/help?set_language=en
    Wait Until Page Contains    Help
    Wait Until Page Contains    Introduction
    Wait Until Page Contains    Registration
    Wait Until Page Contains    Carrying out your risk assessment
    Wait Until Page Contains    Preparation
    Wait Until Page Contains    Identification
    Wait Until Page Contains    Evaluation
    Wait Until Page Contains    Action Plan
    Wait Until Page Contains    Report
    Wait Until Page Contains    What happens next?

Test help headings bg
    Go To    ${PROTOCOL}://${SERVER}/bg/help?set_language=bg
    Wait Until Page Contains    Помощ
    Wait Until Page Contains    Въведение
    Wait Until Page Contains    Регистрация
    Wait Until Page Contains    Как да извършите оценка на риска
    Wait Until Page Contains    Подготовка
    Wait Until Page Contains    Определяне
    Wait Until Page Contains    Оценка
    Wait Until Page Contains    План за действие
    Wait Until Page Contains    Доклад
    Wait Until Page Contains    Какво се случва след това?

Test help headings ca
    Go To    ${PROTOCOL}://${SERVER}/es/help?set_language=ca
    Wait Until Page Contains    Ajuda
    Wait Until Page Contains    Introducció
    Wait Until Page Contains    Registrar-se
    Wait Until Page Contains    Sessions
    Wait Until Page Contains    Preparació
    Wait Until Page Contains    Identificació
    Wait Until Page Contains    Avaluació
    Wait Until Page Contains    Pla d’acció
    Wait Until Page Contains    Informe
    Wait Until Page Contains    Què passa després?

Test help headings cs
    Go To    ${PROTOCOL}://${SERVER}/cz/help?set_language=cs
    Wait Until Page Contains    Nápověda
    Wait Until Page Contains    Úvod
    Wait Until Page Contains    Registrace
    Wait Until Page Contains    Provedení vlastního hodnocení rizik
    Wait Until Page Contains    Příprava
    Wait Until Page Contains    Identifikace
    Wait Until Page Contains    Vyhodnocení
    Wait Until Page Contains    Akční plán
    Wait Until Page Contains    Zpráva
    Wait Until Page Contains    Co bude následovat?

Test help headings de
    Go To    ${PROTOCOL}://${SERVER}/de/help?set_language=de
    Wait Until Page Contains    Hilfe
    Wait Until Page Contains    Einführung
    Wait Until Page Contains    Registrierung
    Wait Until Page Contains    Sitzungen
    Wait Until Page Contains    Vorbereitung
    Wait Until Page Contains    Ermittlung
    Wait Until Page Contains    Bewertung
    Wait Until Page Contains    Aktionsplan
    Wait Until Page Contains    Bericht
    Wait Until Page Contains    Was geschieht als nächstes?

Test help headings el
    Go To    ${PROTOCOL}://${SERVER}/cy/help?set_language=el
    Wait Until Page Contains    Εισαγωγή
    Wait Until Page Contains    Εγγραφή
    Wait Until Page Contains    Εκπόνηση εκτίμησης κινδύνου
    Wait Until Page Contains    Προετοιμασία
    Wait Until Page Contains    Αναγνώριση
    Wait Until Page Contains    Αξιολόγηση
    Wait Until Page Contains    Σχέδιο Δράσης
    Wait Until Page Contains    Έκθεση
    Wait Until Page Contains    Επόμενα Βήματα

Test help headings es
    Go To    ${PROTOCOL}://${SERVER}/es/help?set_language=es
    Wait Until Page Contains    Introducción
    Wait Until Page Contains    Registro
    Wait Until Page Contains    Sesiones
    Wait Until Page Contains    Preparación
    Wait Until Page Contains    Identificación
    Wait Until Page Contains    Evaluación
    Wait Until Page Contains    Plan de Acción
    Wait Until Page Contains    Informe
    Wait Until Page Contains    ¿Qué pasa después?

Test help headings fr
    Go To    ${PROTOCOL}://${SERVER}/fr/help?set_language=fr
    Wait Until Page Contains    Introduction
    Wait Until Page Contains    Inscription
    Wait Until Page Contains    Réaliser votre évaluation en ligne
    Wait Until Page Contains    Préparation
    Wait Until Page Contains    Identification
    Wait Until Page Contains    Estimation
    Wait Until Page Contains    Plan d´action
    Wait Until Page Contains    Rapport
    Wait Until Page Contains    Et ensuite ?

Test help headings lt
    Go To    ${PROTOCOL}://${SERVER}/lt/help?set_language=lt
    Wait Until Page Contains    Įvadas
    Wait Until Page Contains    Registracija
    Wait Until Page Contains    Atlikite rizikos vertinimą
    Wait Until Page Contains    Paruošimas
    Wait Until Page Contains    Nustatymas
    Wait Until Page Contains    Vertinimas
    Wait Until Page Contains    Veiksmų planas
    Wait Until Page Contains    Ataskaita
    Wait Until Page Contains    Kas toliau?

Test help headings lv
    Go To    ${PROTOCOL}://${SERVER}/lv/help?set_language=lv
    Wait Until Page Contains    Ievads
    Wait Until Page Contains    Reģistrācija
    Wait Until Page Contains    Riska novērtējums
    Wait Until Page Contains    Sagatavošanās
    Wait Until Page Contains    Identifikācija
    Wait Until Page Contains    Novērtēšana
    Wait Until Page Contains    Rīcības plāns
    Wait Until Page Contains    Pārskats
    Wait Until Page Contains    Kas notiks tālāk?

Test help headings nl-be
    Go To    ${PROTOCOL}://${SERVER}/be/help?set_language=nl-be
    # Wait Until Page Contains    ? (Help in nl-be)    ? (Help in nl-be)
    Wait Until Page Contains    Inleiding
    Wait Until Page Contains    Registratie
    Wait Until Page Contains    Uw risicoanalyse uitvoeren
    Wait Until Page Contains    Voorbereiding
    Wait Until Page Contains    Identificatie
    Wait Until Page Contains    Evaluatie
    Wait Until Page Contains    Actieplan
    Wait Until Page Contains    Rapport
    Wait Until Page Contains    Wat gebeurt er vervolgens?

Test help headings pt
    Go To    ${PROTOCOL}://${SERVER}/pt/help?set_language=pt
    Wait Until Page Contains    Ajuda
    Wait Until Page Contains    Registo
    Wait Until Page Contains    Realizar a sua avaliação de riscos
    Wait Until Page Contains    Preparação
    Wait Until Page Contains    Identificação
    Wait Until Page Contains    Avaliação
    Wait Until Page Contains    Plano de Ação
    Wait Until Page Contains    Relatório
    Wait Until Page Contains    O que acontece a seguir?

Test help headings sk
    Go To    ${PROTOCOL}://${SERVER}/sk/help?set_language=sk
    Wait Until Page Contains    Pomocník
    Wait Until Page Contains    Úvod
    Wait Until Page Contains    Registrácia
    Wait Until Page Contains    Stretnutia
    Wait Until Page Contains    Príprava
    Wait Until Page Contains    Identifikácia
    Wait Until Page Contains    Hodnotenie
    Wait Until Page Contains    Plán činnosti
    Wait Until Page Contains    Spravodajstvo
    Wait Until Page Contains    Čo sa bude diať ďalej?

Test help headings sl
    Go To    ${PROTOCOL}://${SERVER}/si/help?set_language=sl
    Wait Until Page Contains    Pomoč
    Wait Until Page Contains    Uvod
    Wait Until Page Contains    Registracija
    Wait Until Page Contains    Ocenjevanje tveganja
    Wait Until Page Contains    Priprava
    Wait Until Page Contains    Identifikacija
    Wait Until Page Contains    Ocena
    Wait Until Page Contains    Načrt ukrepov
    Wait Until Page Contains    Poročilo
    Wait Until Page Contains    Kako naprej?

# SV Swedish is not supported
# Test help headings sv
#     Go To    ${PROTOCOL}://${SERVER}/se/help?set_language=sv
#     Wait Until Page Contains    Hjälp
#     Wait Until Page Contains    Introduktion
#     Wait Until Page Contains    Autentisering
#     Wait Until Page Contains    OiRA-verktyg
#     Wait Until Page Contains    Förberedning
#     Wait Until Page Contains    Identifiering
#     Wait Until Page Contains    Utvärdering
#     Wait Until Page Contains    Handlingsplan
#     Wait Until Page Contains    Rapport
#     Wait Until Page Contains    Slutord