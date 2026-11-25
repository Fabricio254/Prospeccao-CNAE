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

## Categorias espelhadas no Google Maps

O seletor **Categoria** no modo **🗺️ Google Maps** agora inclui os mesmos 13
segmentos de `GRUPOS_CNAE`, além das categorias gerais e da busca personalizada
que já existiam. Cada segmento seleciona automaticamente um termo de pesquisa
adequado para encontrar estabelecimentos no Maps:

| Segmento CNAE | Termo usado na busca do Maps |
|---|---|
| Construção Civil e Obras | construtoras e empresas de construção civil |
| Indústria — Manutenção e Instalação | empresas de manutenção e instalação industrial |
| Energia — Eólica, Elétrica, Óleo e Gás | empresas de energia, petróleo e gás |
| Mineração e Siderurgia | empresas de mineração, siderurgia e metalurgia |
| Transporte e Logística | transportadoras e empresas de logística |
| Agroindústria e Alimentos | agroindústrias e fabricantes de alimentos |
| Eventos, Palcos e Estruturas Temporárias | empresas de eventos, palcos e estruturas temporárias |
| Portos e Terminais | empresas portuárias, operadores de terminais e serviços marítimos |
| Engenharia Civil e Arquitetura | empresas de engenharia civil e escritórios de arquitetura |
| Escritórios de Contabilidade | escritórios de contabilidade |
| Hotéis e Apart-hotéis | hotéis e apart-hotéis |
| Administradoras de Condomínios | administradoras de condomínios |
| Escolas Particulares | escolas particulares e colégios |

O Maps usa pesquisa textual: os resultados podem incluir empresas relacionadas,
mas não são filtrados nem verificados pelo código CNAE. Em particular, confirme
se escolas são particulares e se empresas de imóveis realmente administram
condomínios.

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

## Publicação

- Repositório: `Fabricio254/Prospeccao-CNAE`.
- Branch atualizada: `main`.
- Commits publicados:
  - `37c95cd` — adiciona os novos setores CNAE;
  - `ef80fb8` — registra a publicação;
  - atualização atual — espelha os 13 setores CNAE nas categorias do Google Maps.
- Aplicação: <https://prospeccao-cnae.streamlit.app/>.

Após o envio, a URL carregou a tela de autenticação do Streamlit. Os novos
setores ainda não foram conferidos visualmente após o login; não foi feito
login nesta sessão.

## Validação

- [x] Conferência dos códigos e descrições no serviço de subclasses CNAE do IBGE.
- [x] Verificação sintática do arquivo Python.
- [x] Teste de que os quatro segmentos e os 14 códigos novos aparecem no
  catálogo e na lista agregada de CNAEs.
- [x] Teste de que os 13 grupos CNAE têm exatamente um termo de busca Maps e
  nenhum segmento ficou faltando.
- [x] Publicação na branch `main` e verificação de que a aplicação responde.
- [ ] Conferência dos novos segmentos dentro da interface autenticada.
