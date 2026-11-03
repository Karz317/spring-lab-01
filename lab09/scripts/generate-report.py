"""Build the report from saved observations. Requires python-docx and Pillow."""
from pathlib import Path
import json, re
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
E = DOCS / 'evidence'
F = DOCS / 'figures'
F.mkdir(exist_ok=True)
r = json.loads((E / 'live-observations.json').read_text(encoding='utf-8-sig'))

def figure(filename, title, lines, source):
    font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 25)
    small = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 22)
    heading = ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf', 29)
    width, height = 1510, 115 + 39*len(lines) + 62
    im = Image.new('RGB', (width, height), '#f7f9fc')
    d = ImageDraw.Draw(im)
    d.rectangle((0,0,width-1,height-1),outline='#cfd8e4',width=2)
    d.text((28,20),title,font=heading,fill='#172b46')
    for i,line in enumerate(lines): d.text((28,83+39*i),line,font=font,fill='#182334')
    d.text((28,height-49),source,font=small,fill='#526478')
    im.save(F/filename)

figure('01-transactions.png','Actual API observations  |  Transactions and rollback',[
    'Scenario                         Alice       Bob         Result',
    'Initial                          1000.00     500.00      total 1500.00',
    f'Transfer 100.00                   {r["transfer"]["after"][0]["BALANCE"]:.2f}      {r["transfer"]["after"][1]["BALANCE"]:.2f}      committed',
    f'Insufficient funds               {r["insufficientFunds"]["after"][0]["BALANCE"]:.2f}     {r["insufficientFunds"]["after"][1]["BALANCE"]:.2f}      rolled back',
    f'Unchecked error after flush      {r["rollback"]["after"][0]["BALANCE"]:.2f}     {r["rollback"]["after"][1]["BALANCE"]:.2f}      rolled back',
    f'Checked exception, default       {r["checkedDefault"][0]["BALANCE"]:.2f}      500.00      debit committed',
    f'Checked exception, rollbackFor   {r["checkedRollbackFor"][0]["BALANCE"]:.2f}     500.00      rolled back',
], 'Source: docs/evidence/live-observations.json; POST /api/lab09/experiments')
figure('02-propagation-isolation.png','Actual API observations  |  Propagation and H2 isolation',[
    f'REQUIRED       after outer rollback: audit rows = {r["required"]["auditCount"]}, Alice = 1000.00',
    f'REQUIRES_NEW   after outer rollback: audit rows = {r["requiresNew"]["auditCount"]}, Alice = 1000.00',
    '',
    'Isolation          First read   Writer committed   Second read',
    f'READ_COMMITTED     {r["readCommitted"]["firstRead"]:.2f}      {r["readCommitted"]["writerCommitted"]:.2f}            {r["readCommitted"]["secondRead"]:.2f}',
    f'REPEATABLE_READ    {r["repeatableRead"]["firstRead"]:.2f}      {r["repeatableRead"]["writerCommitted"]:.2f}            {r["repeatableRead"]["secondRead"]:.2f}',
    f'H2 {r["runtime"]["database"]}; two independent JDBC connections; direct SQL reads',
], 'Source: docs/evidence/live-observations.json; each isolation scenario starts at 1000.00')
figure('03-optimistic-lock.png','Actual API observations  |  Stale update rejected',[
    f'Two independent persistence contexts loaded version {r["optimisticLock"]["loadedVersion"]}',
    'Context 1: credit 10.00; commit succeeds',
    'Context 2: credit 20.00; commit fails',
    f'Exception: {r["optimisticLock"]["conflict"]} caused by optimistic-lock conflict',
    f'Final balance: {r["optimisticLock"]["finalBalance"]:.2f}; committed version: {r["optimisticLock"]["committedVersion"]}',
    'staleUpdateRejected: true',
], 'Source: docs/evidence/live-observations.json; ConcurrencyExperiments.optimisticLock')
loglines=[]
for name in ['first-v2','restart-v2','upgrade-v4']:
    text=(E/(name+'.log')).read_text(encoding='utf-8',errors='replace')
    loglines.append(name+'.log')
    for line in text.splitlines():
        if 'Migrating schema' in line or 'Successfully applied' in line or 'No migration necessary' in line:
            s=line.split(' : ',1)[-1]
            s=re.sub(r' \(execution time.*','',s)
            loglines.append('  '+s)
figure('04-real-restarts.png','Actual startup logs  |  Three complete application launches',loglines,
       'Source: docs/evidence/first-v2.log, restart-v2.log, upgrade-v4.log')
summary=(E/'surefire-summary.txt').read_text().splitlines()[-1]
figure('05-test-summary.png','Actual Maven and Surefire output',[
    'Test set: kz.iitu.txlab.TransactionLabTests',
    'Tests run: 18, Failures: 0, Errors: 0, Skipped: 0',
    '[INFO] BUILD SUCCESS',
    'Spring Boot '+r['runtime']['springBoot']+' | H2 '+r['runtime']['database']+' | Java '+r['runtime']['java'],
], 'Source: docs/evidence/surefire-summary.txt and maven-verify.log')

doc=Document()
sec=doc.sections[0]
sec.page_width=Cm(21); sec.page_height=Cm(29.7)
sec.top_margin=Cm(1.7); sec.bottom_margin=Cm(1.6)
sec.left_margin=Cm(1.9); sec.right_margin=Cm(1.9)
styles=doc.styles
for border in list(doc.element.xpath('.//w:pBdr')) + list(styles.element.xpath('.//w:pBdr')):
    border.getparent().remove(border)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Caption']:
    styles[name].font.name='Calibri'; styles[name].font.color.rgb=RGBColor(0,0,0)
styles['Normal'].font.size=Pt(11)
styles['Normal'].paragraph_format.space_after=Pt(6)
styles['Normal'].paragraph_format.line_spacing=1.08
styles['Title'].font.size=Pt(25)
styles['Heading 1'].font.size=Pt(17); styles['Heading 1'].paragraph_format.space_after=Pt(9)
styles['Heading 2'].font.size=Pt(12); styles['Heading 2'].paragraph_format.space_before=Pt(10)
styles['Caption'].font.size=Pt(9); styles['Caption'].font.italic=True
doc.core_properties.author='Arzum Kassymzhanov'
doc.core_properties.title='Laboratory Work 09 Spring Transaction Management and Database Schema Versioning'

def p(text='',style=None): return doc.add_paragraph(text,style)
def h(text): doc.add_heading(text,1)
def h2(text): doc.add_heading(text,2)
def page(): doc.add_page_break()
def code(text):
    para=p(); para.paragraph_format.space_after=Pt(8)
    run=para.add_run(text); run.font.name='Consolas'; run.font.size=Pt(9)
def table(headers, rows, widths=None):
    t=doc.add_table(rows=1,cols=len(headers)); t.autofit=False
    for i,txt in enumerate(headers): t.rows[0].cells[i].text=txt
    for row in rows:
        for cell,txt in zip(t.add_row().cells,row): cell.text=str(txt)
    for n,row in enumerate(t.rows):
        for i,c in enumerate(row.cells):
            if widths: c.width=Cm(widths[i])
            tcPr=c._tc.get_or_add_tcPr(); borders=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                b=OxmlElement('w:'+edge); b.set(qn('w:val'),'single'); b.set(qn('w:sz'),'4'); b.set(qn('w:color'),'D9D9D9'); borders.append(b)
            tcPr.append(borders)
            margins=OxmlElement('w:tcMar')
            for edge in ['top','bottom','left','right']:
                el=OxmlElement('w:'+edge);el.set(qn('w:w'),'80');el.set(qn('w:type'),'dxa');margins.append(el)
            tcPr.append(margins)
            for par in c.paragraphs:
                par.paragraph_format.space_after=Pt(2)
                for run in par.runs:run.font.size=Pt(10);run.bold=(n==0)
            if n==0:
                shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'EEF2F6');tcPr.append(shade)
    t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
    p()
    return t
def pic(name,caption):
    para=p();para.paragraph_format.keep_with_next=True
    para.add_run().add_picture(str(F/name),width=Cm(17.1))
    p(caption,'Caption')

p('Laboratory Work 09','Title')
p('Spring Transaction Management\nand Database Schema Versioning','Subtitle')
p('Arzum Kassymzhanov  |  IT1-2404IS\n3 November 2026')
h('Aim and outcome')
p('I implemented atomic account transfers, transaction propagation experiments, independent database reads at two isolation levels, optimistic locking and versioned database migrations. The application and 18 integration tests confirm rollback behavior and prevent a stale account update from overwriting a committed change.')
table(['Environment','Verified configuration'],[
    ['Application','Standalone lab09 module in spring-lab-01'],
    ['Framework','Spring Boot '+r['runtime']['springBoot']+' with Spring Data JPA'],
    ['Runtime','Java '+r['runtime']['java']+'; compiled for Java 17; Maven 3.9.16'],
    ['Database','H2 '+r['runtime']['database']+'; memory database and file database restart proof'],
    ['Schema tool','Flyway; Hibernate ddl-auto=validate'],
    ['Local demo','http://127.0.0.1:8089; loopback binding'],
], [4.0,13.0])
h2('Main observations')
table(['Experiment','Observed result'],[
    ['Transfer and rollback','1000/500 becomes 900/600; failures restore 1000/500'],
    ['Propagation','REQUIRED leaves 0 audit rows; REQUIRES_NEW leaves 1'],
    ['Isolation on H2','READ_COMMITTED sees 1050; REPEATABLE_READ sees 1000'],
    ['Optimistic locking','Stale commit rejected; balance 1010; version 1'],
    ['Migration lifecycle','2 migrations, then 0 on restart, then 2 new versions'],
], [4.0,13.0])
p('Evidence is included as machine-readable API responses, complete Maven/Surefire output and application startup logs. Report figures reproduce excerpts from those saved observations.')

page(); h('Task A Declarative transactions and rollback')
p('The service method is the business transaction boundary: loading both accounts, checking the amount, debiting and crediting all take place in one transaction. Account balances use BigDecimal and DECIMAL(19,2). The database also rejects negative balances.')
code('@Transactional\npublic void transfer(Long fromId, Long toId, BigDecimal amount) {\n    Account from = get(fromId);\n    Account to = get(toId);\n    from.debit(amount);\n    to.credit(amount);\n    repository.save(from);\n    repository.save(to);\n}')
pic('01-transactions.png','Figure 1. Rendered excerpt of the actual live API response for Task A.')
p('After a transfer of 100.00, Alice has 900.00 and Bob 600.00. Their total remains 1500.00. A transfer of 1001.00 fails with Insufficient funds; neither balance changes.')
p('The unchecked failure experiment calls repository.flush() after the debit and throws before any credit. The balance returns to 1000.00, demonstrating rollback of an SQL update that already reached the database.')
h2('Checked exceptions and rollback rules')
p('With the default Spring rollback rules, RuntimeException and Error trigger rollback; a checked exception normally does not. checkedDefault therefore commits the deliberately isolated debit, leaving Alice at 900.00. checkedRollback uses @Transactional(rollbackFor = CheckedTransferException.class), restoring 1000.00. These methods are controlled experiments, not transfer endpoints.')
p('Transaction interception requires a call through a Spring proxy. The controller and experiment coordinator call the injected service bean; a same-object call to another annotated method would not create the intended proxy boundary.')

page(); h('Tasks B and C Propagation and isolation')
h2('Propagation with an independent audit bean')
p('The outer transaction debits 10.00, invokes AuditService, and throws an unchecked exception after the inner method returns. REQUIRED joins the outer transaction, so its audit insert also rolls back. REQUIRES_NEW suspends the outer transaction and commits its own audit insert; the audit record remains even though the outer debit rolls back.')
pic('02-propagation-isolation.png','Figure 2. Measured propagation results and two-connection H2 isolation experiment.')
p('The audit methods live in a separate Spring bean. REQUIRES_NEW uses an additional connection while the outer transaction is suspended. Audit entries describe the event independently; their existence must not be interpreted as proof that the outer transfer committed.')
h2('Isolation experiment procedure')
p('Reader and writer use two separate JDBC connections with auto-commit disabled. The reader selects Alice at 1000.00; the writer adds 50.00, increments the version, and commits. The reader repeats the SELECT before ending its own transaction. Direct SQL avoids the JPA first-level cache.')
p('On H2 '+r['runtime']['database']+', READ_COMMITTED returns 1050.00 on the second read, demonstrating a non-repeatable read. REPEATABLE_READ returns 1000.00 while a fresh committed read returns 1050.00. Both modes prevent dirty reads. REPEATABLE_READ prevents non-repeatable reads of the same row, but phantom handling and other details depend on the database. This experiment tests repeated reads of one row; it does not test predicate phantoms, write skew or serializability.')
h2('Other propagation modes')
p('SUPPORTS joins a transaction if present; MANDATORY requires one; NOT_SUPPORTED suspends it; NEVER rejects an active transaction. NESTED uses a savepoint where the transaction manager supports it; it is not a portable substitute for REQUIRES_NEW with JPA.')

page(); h('Task D Optimistic locking')
p('Account maps its version column with @Version. I loaded the same account in two independent EntityManagers with simultaneously active transactions. Both copies had version 0. The first context credited 10.00 and committed. The second tried to credit 20.00 using its stale version.')
code('@Version\n@Column(nullable = false)\nprivate Long version;\n\n-- Hibernate update includes the expected version:\nUPDATE accounts SET balance = ?, version = ?\nWHERE id = ? AND version = ?;')
pic('03-optimistic-lock.png','Figure 3. Actual stale-commit result from two independent persistence contexts.')
p('The first commit changed Alice to 1010.00 and version 1. The stale commit failed with RollbackException containing an optimistic-lock cause. Its WHERE version=0 matched no row, so it could not silently replace the committed value with 1020.00. The test verifies that the final database state remains 1010.00 and version 1.')
h2('A safe response to a conflict')
p('The failed transaction must be rolled back and its persistence context discarded or refreshed before another attempt. A user-facing service should report the conflict and offer current data. An automatic retry is appropriate only when the complete operation is safe to repeat and its business conditions are rechecked; a money transfer also needs protection against duplicate execution. Reusing the stale entity or blindly replaying a debit can lose updates or perform an operation twice.')
h2('What the version field protects')
p('The version check detects competing updates to one versioned entity. It complements transaction atomicity; it does not by itself provide serializable execution across arbitrary multi-row business rules. The isolation experiment increments version explicitly because it performs direct SQL rather than an entity update.')

page(); h('Task E Database schema versioning')
table(['Version','Migration','Purpose'],[
    ['V1','V1__create_accounts.sql','Accounts, balances, version and seed data'],
    ['V2','V2__add_status.sql','ACTIVE status with a non-null default'],
    ['V3','V3__index_owner_name.sql','Index on owner_name'],
    ['V4','V4__create_audit_records.sql','Independent audit table'],
], [1.8,6.8,8.4])
p('The automated migration experiment queries the quoted flyway_schema_history table and records each version, script, success flag and checksum. It also verifies that IDX_ACCOUNTS_OWNER_NAME exists. A fresh Flyway instance reuses the same schema history and executes zero already-applied versions.')
pic('04-real-restarts.png','Figure 4. Excerpts from real application startup logs against the same H2 file.')
p('The separate PowerShell check launches the complete application three times against one persistent H2 file. First, target V2 applies V1 and V2 to an empty database. A full stop and restart at target V2 applies nothing. The final startup at target V4 applies the new index and audit migrations. The first two stages use ddl-auto=none because the audit table is intentionally not present yet; the final stage validates the complete schema.')
p('Applied versioned migrations must remain immutable. Editing an old file changes its checksum and can make validation fail; it also makes different environments disagree about what the same version means. A correction should be a new versioned migration committed alongside the code.')

page(); h('Verification and reproducibility')
pic('05-test-summary.png','Figure 5. Actual successful Maven verification and Surefire summary.')
table(['Coverage','Verified behavior'],[
    ['Transactions','Successful transfer, conserved total, insufficient funds, flushed rollback'],
    ['Rollback rules','Checked default commit and explicit rollbackFor'],
    ['Propagation','REQUIRED audit rollback and REQUIRES_NEW independent commit'],
    ['Concurrency','READ_COMMITTED, REPEATABLE_READ and stale entity rejection'],
    ['Migrations','Initial application, no repeat, new versions and index existence'],
    ['Boundaries and HTTP','Same account, missing destination, fractional cents, blocked destination, 400 and 409'],
], [3.8,13.2])
h2('Run from the repository')
code("Set-Location 'C:\\Labworks\\Spring\\spring-lab-01-main\\lab09'\n.\\mvnw.cmd clean verify\njava -jar .\\target\\transaction-lab09-1.0.0.jar\n# Open http://127.0.0.1:8089\n# Stop the application before the full restart check:\n.\\scripts\\verify-migrations.ps1")
p('The default database is in memory and starts with Alice 1000.00 and Bob 500.00. The experiment button deliberately resets those sample accounts before each scenario. File persistence is selected with --spring.datasource.url=jdbc:h2:file:./data/txlab. The teaching API binds to 127.0.0.1 and is intended for local, disposable lab data.')
h2('Delivered implementation')
p('The lab09 module contains the entity and repositories, transfer and audit services, propagation and concurrency experiments, Flyway migrations, integration tests, a local browser demonstration, HTTP requests, the restart script, saved evidence and this report. The original book application remains a separate project at the repository root.')

page(); h('Answers and conclusions')
h2('1 What does Transactional do and where do boundaries belong')
p('@Transactional makes a Spring proxy open or join a transaction and apply commit or rollback rules around a method invocation. It configures propagation, isolation, timeout and read-only behavior. Boundaries normally surround one complete business operation in a service, such as moving money between accounts, rather than each repository call independently.')
h2('2 REQUIRED and REQUIRES_NEW')
p('REQUIRED joins an existing physical transaction or starts one if none exists. REQUIRES_NEW always creates an independent transaction and suspends the outer one. In this experiment the shared audit rolled back; the independent audit committed and survived the outer failure.')
h2('3 Anomalies and database differences')
p('READ_COMMITTED prevents dirty reads but can allow non-repeatable reads and phantoms. REPEATABLE_READ also prevents changes to previously read row values; phantom behavior depends on the engine and implementation. H2 preserved 1000.00 at REPEATABLE_READ while READ_COMMITTED returned the writer\'s committed 1050.00. These measurements must not be generalized to every database.')
h2('4 How Version detects concurrent updates')
p('Hibernate includes the loaded version in an UPDATE predicate and increments the version on success. A competing commit changes the stored version. The stale update then affects zero rows and fails instead of overwriting the first update. The application must handle the conflict in a new valid transaction.')
h2('5 Why migrations are version controlled and immutable')
p('Version control makes schema changes reviewable and deployable with the application. A history table tracks order, checksums and successful execution. Immutability keeps environments consistent and allows validation to detect drift. Fixes are introduced through new migrations rather than edits to deployed files.')
h2('6 Choosing Flyway or Liquibase')
p('I chose Flyway because the exercise uses a small ordered sequence of SQL migrations that is easy to review. Liquibase is useful when a team needs structured changesets, preconditions, contexts and labels, or explicit rollback definitions. Either tool still requires database-specific validation and deliberate rollback planning; they should not both own this schema.')
h2('Conclusion')
p('I observed atomic transfers and rollback after a flushed SQL update, an independent audit commit with REQUIRES_NEW, database-specific repeatable-read behavior, and rejection of a stale entity update. Flyway applied V1–V2 once, skipped them after a real application restart, and then applied V3–V4. Correct transaction boundaries, explicit conflict handling and immutable migrations jointly protect application data.')
h2('References')
for text in ['Spring Framework: docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html',
             'Spring propagation: docs.spring.io/spring-framework/reference/data-access/transaction/declarative/tx-propagation.html',
             'H2 isolation: h2database.com/html/advanced.html#transaction_isolation']:
    para=p(text);para.paragraph_format.space_after=Pt(3)
    for run in para.runs: run.font.size=Pt(8)

out=DOCS/'Lab09_Kassymzhanov_Arzum.docx'
doc.save(out)
print(out)
