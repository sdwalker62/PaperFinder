<script lang="ts">
    let showModal = $state(false);
    let password = $state("");
    let loading = $state(false);
    let resultMessage = $state("");
    let resultError = $state(false);

    async function triggerPipeline() {
        loading = true;
        resultMessage = "";
        resultError = false;

        try {
            const res = await fetch("/api/pipeline", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ password }),
            });

            const data = await res.json();

            if (!res.ok) {
                resultError = true;
                resultMessage = data.message ?? `Error ${res.status}`;
            } else {
                resultMessage = "Pipeline triggered successfully!";
            }
        } catch (err) {
            resultError = true;
            resultMessage = `Network error: ${(err as Error).message}`;
        } finally {
            loading = false;
            password = "";
        }
    }

    function closeModal() {
        showModal = false;
        resultMessage = "";
        resultError = false;
        password = "";
    }
</script>

<button
    class="btn btn-sm btn-outline btn-primary"
    onclick={() => (showModal = true)}
>
    Run Pipeline
</button>

{#if showModal}
    <dialog class="modal modal-open">
        <div class="modal-box">
            <h3 class="text-lg font-bold">Trigger Pipeline</h3>
            <p class="py-2 text-sm text-base-content/60">
                Enter the admin password to run the paper discovery pipeline.
            </p>

            {#if resultMessage}
                <div
                    class="alert {resultError
                        ? 'alert-error'
                        : 'alert-success'} mt-2"
                >
                    <span>{resultMessage}</span>
                </div>
            {/if}

            {#if !resultMessage || resultError}
                <form
                    onsubmit={(e) => {
                        e.preventDefault();
                        triggerPipeline();
                    }}
                    class="mt-4 flex flex-col gap-3"
                >
                    <input
                        type="password"
                        class="input input-bordered w-full"
                        placeholder="Admin password"
                        bind:value={password}
                        disabled={loading}
                        autocomplete="off"
                    />
                    <div class="modal-action">
                        <button
                            type="button"
                            class="btn btn-ghost"
                            onclick={closeModal}
                            disabled={loading}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            class="btn btn-primary"
                            disabled={loading || !password}
                        >
                            {#if loading}
                                <span class="loading loading-spinner loading-sm"
                                ></span>
                                Running…
                            {:else}
                                Run
                            {/if}
                        </button>
                    </div>
                </form>
            {:else}
                <div class="modal-action">
                    <button class="btn" onclick={closeModal}>Close</button>
                </div>
            {/if}
        </div>
        <form method="dialog" class="modal-backdrop">
            <button onclick={closeModal}>close</button>
        </form>
    </dialog>
{/if}
