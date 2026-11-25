# Atualização — Segmentos de prospecção por CNAE

## Objetivo

Adicionar ao seletor **Setor de atividade** quatro segmentos solicitados para a
aplicação ZampaSys — Prospecção de Clientes:

- Escritórios de contabilidade;
- Hotéis;
- Administradoras de condomínios;
- Escolas particulares.

## O que foi alterado

No arquivo `Propescao.py`, foram adicionados quatro grupos ao dicionário
`GRUPOS_CNAE`. A interface já gera o seletor de setores a partir desse
dicionário; por isso, os novos grupos passam a aparecer no mesmo campo
**Setor de atividade**, sem alterar os modos de busca existentes.

Ao escolher um setor, a aplicação apresenta sua descrição e os CNAEs associados
em uma lista multisseleção. Todos os códigos do grupo vêm selecionados por
padrão, mas podem ser desmarcados antes de iniciar a busca. Os códigos também
passam a integrar o dicionário agregado `TODOS_CNAES`.

### Grupos e códigos incluídos

| Setor | CNAE | Atividade |
|---|---:|---|
| Escritórios de Contabilidade | 6920601 | Atividades de contabilidade |
| Escritórios de Contabilidade | 6920602 | Consultoria e auditoria contábil e tributária |
| Hotéis e Apart-hotéis | 5510801 | Hotéis |
| Hotéis e Apart-hotéis | 5510802 | Apart-hotéis |
| Administradoras de Condomínios | 6822600 | Gestão e administração da propriedade imobiliária |
| Escolas Particulares | 8511200 | Educação infantil — creche |
| Escolas Particulares | 8512100 | Educação infantil — pré-escola |
| Escolas Particulares | 8513900 | Ensino fundamental |
| Escolas Particulares | 8520100 | Ensino médio |
| Escolas Particulares | 8531700 | Educação superior — graduação |
| Escolas Particulares | 8532500 | Educação superior — graduação e pós-graduação |
| Escolas Particulares | 8533300 | Educação superior — pós-graduação e extensão |
| Escolas Particulares | 8541400 | Educação profissional de nível técnico |
| Escolas Particulares | 8542200 | Educação profissional de nível tecnológico |

Os códigos e descrições foram conferidos no serviço de subclasses CNAE do IBGE.

## Observação sobre escolas particulares

O CNAE indica a atividade econômica, mas não diferencia por si só uma
instituição pública de uma particular. O grupo reúne subclasses educacionais
relevantes; confirme a natureza e a situação cadastral das empresas nos dados
consultados antes de usar os resultados como uma lista exclusiva de escolas
privadas.

Da mesma forma, o CNAE 6822600 identifica gestão e administração da propriedade
imobiliária em geral; não separa exclusivamente administradoras de condomínios.

## Arquivos

- `Propescao.py` — inclusão dos quatro grupos no catálogo de segmentos.
- `ALTERACOES_PROSPECCAO_CNAE.md` — registro desta alteração, códigos e ressalvas.

Nenhuma dependência foi adicionada ou alterada como parte desta implementação.

## Validação

- [x] Conferência dos códigos e descrições no serviço de subclasses CNAE do IBGE.
- [x] Verificação sintática do arquivo Python.
- [x] Teste de que os quatro segmentos e os 14 códigos novos aparecem no
  catálogo e na lista agregada de CNAEs.
- [ ] Publicação e conferência na aplicação Streamlit.
