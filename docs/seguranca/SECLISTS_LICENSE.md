# Lista local de senhas comuns — proveniência e licença

[SecLists](https://github.com/danielmiessler/SecLists), arquivo
`Passwords/Common-Credentials/xato-net-10-million-passwords-1000000.txt`,
revisão `c205c36a445bff37f8e58a9ec829105cd4975c58`, SHA-256 da fonte
`424a3e03a17df0a2bc2b3ca749d81b04e79d59cb7aeec8876a5a3f308d0caf51`.

A lista embarcada contém 10.898 digests SHA-256 das entradas distintas após
casefold cujo tamanho atende à política de 15–128 caracteres. As demais entradas
já são recusadas pelo tamanho. Não são hashes de credenciais de contas do produto:
as credenciais continuam Argon2id. Casefold serve somente à consulta da lista;
senha verificada não é normalizada. Nenhuma senha é enviada a serviço externo.
Essa lista finita não garante ausência em vazamentos nem substitui demais
controles. Não contém usuários, e-mails ou dados da pesquisa.

Regeneração explícita, com fonte imutável e checksum obrigatório:
`python3 scripts/build_password_blocklist.py`. Runtime e testes não baixam a lista.
Gerador: [script](../../scripts/build_password_blocklist.py); consumidor:
[política](../../stroop/domain/local_auth.py). Diretriz geral:
[OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html).

Licença da fonte e da lista derivada:

```text
MIT License

Copyright (c) 2018 Daniel Miessler

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```
